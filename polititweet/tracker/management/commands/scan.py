import tweepy
import random
import requests
import os
import time
import json

from django.core.management.base import BaseCommand, CommandError
from ...models import Tweet, User
from django.conf import settings
import logging

import pytz
from datetime import datetime

local_timezone = pytz.timezone('America/Argentina/Buenos_Aires')


logger = logging.getLogger('django')

class Command(BaseCommand):
    help = "Update database entries of all followed users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--infinite",
            action="store_true",
            dest="repeat",
            help="Just keep updating forever",
        )

    def handle(self, *args, **options):
        def scan():
            self.stdout.write(f"{datetime.now(local_timezone)} - Connecting to Twitter...")
            logger.info(f"{datetime.now(local_timezone)} - Connecting to Twitter...")
            auth = tweepy.OAuthHandler(
                settings.TWITTER_CREDENTIALS["consumer_key"],
                settings.TWITTER_CREDENTIALS["consumer_secret"],
            )
            auth.set_access_token(
                settings.TWITTER_CREDENTIALS["access_token"],
                settings.TWITTER_CREDENTIALS["access_secret"],
            )
            api = tweepy.API(
                auth,
                wait_on_rate_limit=True
            )

            following = get_politicians_twids_list(api)
            #following = [member.id for member in tweepy.Cursor(api.get_list_members, list_id=int(settings.TWITTER_LIST_ID)).items()]
            #following = api.get_friend_ids()
            self.stdout.write("Connected to Twitter.")
            logger.info(f"{datetime.now(local_timezone)} - Connected to Twitter.")

            self.stdout.write("Starting update on %s users..." % str(len(following)))
            logger.info(f"{datetime.now(local_timezone)} - Starting update on %s users..." % str(len(following)))

            users = User.objects.all()
            for user in users:
                if user.user_id not in following:
                    if user.monitored:
                        user.monitored = False
                        user.save()
                        logger.info("Marked %s as unmonitored!" % str(user.user_id))
                else:
                    if not user.monitored:
                        user.monitored = True
                        user.save()
                        logger.info("Marked %s as monitored!" % str(user.user_id))
            completed = 0
            new_accounts = [
                id for id in following if id not in [user.user_id for user in users]
            ]
            flagged_accounts = [
                user.user_id for user in User.objects.filter(flagged=True)
            ]
            random.shuffle(following)  # shuffle order to get even coverage
            iteration_count = 0
            for id in (
                new_accounts
                + flagged_accounts
                + [id for id in following if id not in flagged_accounts + new_accounts]
            ):
                iteration_count += 1
                if iteration_count % 250 == 0: # Cada 250 cuentas, hago una pausa de 5 minutos (por la api de tw)
                    logger.info(
                            "********** Waiting 5 minutes to avoid Twitter API overloading... **********"
                        )
                    time.sleep(300)

                try:
                    user_data = None
                    try:
                        user_data = api.get_user(user_id=id)
                    except tweepy.TweepyException as e:
                        self.stderr.write(str(e))
                        logger.error(
                            str(e)
                        )
                        continue  # important to continue, and to _not_ mark all tweets as deleted
                    try:
                        user = User.objects.get(user_id=id)
                        self.stdout.write(
                            "User @%s already exists; updating record..."
                            % user_data.screen_name
                        )
                        logger.info(
                            "User @%s already exists; updating record..."
                            % user_data.screen_name
                        )
                        user.full_data = user_data._json
                        user.deleted_count = Tweet.objects.filter(
                            user=user, deleted=True
                        ).count()
                        user.save()
                        upsertTweets(
                            api.user_timeline(user_id=user.user_id, count=200), user
                        )
                    except User.DoesNotExist as e:  # does not exist; TODO: use more specific error
                        self.stdout.write(
                            "User @%s does not exist; creating record..."
                            % user_data.screen_name
                        )
                        logger.info(
                            "User @%s does not exist; creating record..."
                            % user_data.screen_name
                        )
                        user = User(user_id=id, full_data=user_data._json)
                        user.save()
                        upsertTweets(getAllStatuses(api, user), user)
                    if hasAccountDeletedTweet(api, user, user_data):
                        self.stdout.write(
                            "Also checking @%s for deleted tweets..."
                            % user_data.screen_name
                        )
                        logger.info(
                            "Also checking @%s for deleted tweets..."
                            % user_data.screen_name
                        )
                        deleted_count = scanForDeletedTweet(api, user)
                        self.stdout.write(
                            self.style.SUCCESS(
                                "Found %s new deleted tweets for @%s"
                                % (str(deleted_count), user_data.screen_name)
                            )
                        )
                        logger.info(
                            self.style.SUCCESS(
                                "Found %s new deleted tweets for @%s"
                                % (str(deleted_count), user_data.screen_name)
                            )
                        )
                        user.flagged = False
                        user.save()
                    completed += 1
                except Exception as e:
                    self.stderr.write(
                        "Encountered an error while scanning %s: %s" % (str(id), str(e))
                    )
                    continue
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully updated @%s (%s/%s)."
                        % (user_data.screen_name, str(completed), str(len(following)))
                    )
                )
                logger.info(
                    self.style.SUCCESS(
                        "Successfully updated @%s (%s/%s)."
                        % (user_data.screen_name, str(completed), str(len(following)))
                    )
                )
            self.stdout.write(
                self.style.SUCCESS(
                    "Finished refreshing %s accounts." % str(len(following))
                )
            )
            logger.info(
                self.style.SUCCESS(
                    "Finished refreshing %s accounts." % str(len(following))
                )
            )

        scan()
        while options["repeat"]:
            scan()


def get_politicians_twids_list(api):
    """
    Function que obtiene la lista de ids de las cuentas cuentas de politicos a observar
    """
    AIRTABLE_TOKEN=settings.AIRTABLE_TOKEN
    AIRTABLE_BASE_ID=settings.AIRTABLE_BASE_ID
    AIRTABLE_TABLE_ID=settings.AIRTABLE_TABLE_ID
    url=f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    headers = {
        'Authorization': f'Bearer {AIRTABLE_TOKEN}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    errors_count = 0
    cantidad_total = 0

    records_to_update = []
    politicians_twids = []
    # Mientras la respuesta sea exitosa...
    while response.status_code == 200:
        politicians_records = response.json()['records']
        cantidad_total += len(politicians_records)

        # Reviso todos por si falta user_id
        for record in politicians_records:
            if 'user_name' in record['fields']: # Si no es un record vacio

                if not 'user_id' in record['fields']:
                    try:
                        # Busco user id en Tweepy
                        user = api.get_user(screen_name=record['fields']['user_name'][1:]) # [1:] para quitar @
                        records_to_update.append(
                            {
                                "id": record['id'],
                                "fields": {
                                    "user_id": user.id_str
                                }
                            }
                        )
                    except Exception as e:
                        logger.error(str(e))
                        errors_count += 1
                else:
                    politicians_twids.append(int(record['fields']['user_id']))

                # Max de records a actualizar en un request de airtable es 10
                # Corto (y actualizo en airtable) si llegue a esa cantidad o si llegue al ultimo de la ultima page con actualizaciones pendientes
                if ((len(records_to_update) == 10) or
                    (len(records_to_update) > 0 and record == politicians_records[-1] and 'offset' not in response.json())):
                    data = {
                        'records': records_to_update
                    }

                    airtable_response = requests.patch(url, headers=headers, data=json.dumps(data))

                    if airtable_response.status_code == 200:
                        new_ids = [int(record['fields']['user_id']) for record in airtable_response.json()['records']]
                        politicians_twids += new_ids
                        records_to_update = []
                    else:
                        logger.error(airtable_response.text) 

        # Que exista una key de offset significa que aun quedan paginas (de 100 elementos c/u) por traer.
        # La ultima pagina no tiene key de offset. Si es la ultima pag, corto el while y no busco mas
        if 'offset' not in response.json(): break

        # Establezco el nuevo offset como parametro
        params = {
            'offset': response.json()['offset']
        }
        time.sleep(0.5) # Pausa de medio segundo entre consultas para no sobrecargar la api de Airtable
        response = requests.get(url, headers=headers, params=params)

    logger.info(f'Cantidad total records airtable: {cantidad_total}')
    logger.info(f'Ids obtenidos: {len(politicians_twids)}')
    logger.info(f'Errores: {errors_count}')

    return politicians_twids


def hasAccountDeletedTweet(api, user_db, user_data):
    if user_db.flagged:
        return True
    if user_data.statuses_count < user_db.full_data["statuses_count"]:
        return True
    latest_known_status = 0
    try:
        latest_known_status = user_db.full_data["status"]["id"]
    except:  # not the prettiest...
        pass
    tweets_since = getAllStatuses(api, user_db, since=latest_known_status)
    return (
        user_data.statuses_count - len(tweets_since)
        < user_db.full_data["statuses_count"]
    )


def upsertTweets(tweets, user):
    for tweet in tweets:
        try:
            tweet_db = Tweet.objects.get(tweet_id=tweet.id)
            tweet_db.full_data = tweet._json
            tweet_db.save()
        except Tweet.DoesNotExist:
            tweet_db = Tweet(tweet_id=tweet.id, full_data=tweet._json, user=user)
            tweet_db.save()


def getAllStatuses(api, user, since=None):
    tweets = []
    new_tweets = api.user_timeline(user_id=user.user_id, count=200, since_id=since)
    tweets.extend(new_tweets)
    while len(new_tweets) > 0:
        oldest = tweets[-1].id - 1
        new_tweets = api.user_timeline(
            user_id=user.user_id, count=200, max_id=oldest, since_id=since
        )
        tweets.extend(new_tweets)
    return tweets


def scanForDeletedTweet(api, user):
    known_tweets = Tweet.objects.filter(user=user, hibernated=False)
    found_tweets = sorted(getAllStatuses(api, user), key=lambda k: k.id)
    found_ids = [tweet.id for tweet in found_tweets]
    minimum_id = found_tweets[0].id
    total_deleted = 0
    for tweet in known_tweets:
        if tweet.tweet_id < minimum_id:
            if not tweet.hibernated:
                tweet.hibernated = True
                tweet.save()
            continue
        if tweet.tweet_id not in found_ids and not tweet.deleted:
            try:
                api.get_status(tweet.tweet_id)
            except tweepy.TweepError as e:
                if e.api_code == 144:
                    tweet.deleted = True
                    tweet.save()
                    logger.info(
                        "Found deleted tweet: %s by @%s"
                        % (str(tweet.tweet_id), user.full_data["screen_name"])
                    )
                    total_deleted += 1
                else:
                    raise e
        else:
            if tweet.deleted:
                tweet.deleted = False
                tweet.save()
    return total_deleted
