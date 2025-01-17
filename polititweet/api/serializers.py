from rest_framework import serializers

from tracker.models import User, Tweet


class DeletedTweetSerializer(serializers.ModelSerializer):
    '''Serializer for deleted tweets.'''
    likely_typo = serializers.ReadOnlyField()
    is_retweet = serializers.ReadOnlyField()
    deleted_after_time_humanized = serializers.ReadOnlyField()
    created_at = serializers.SerializerMethodField()
    retweet_link = serializers.SerializerMethodField()
    tweet_id = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    class Meta:
        model = Tweet
        exclude = ['full_data', 'search_vector', 'hibernated']
        depth = 1

    def get_created_at(self, obj):
        return str(obj.datetime())
    
    def get_tweet_id(self, obj):
        return obj.full_data['id_str']

    def get_retweet_link(self, obj):
        if obj.is_retweet:
            retweeted_status = obj.full_data['retweeted_status']
            retweeted_user_name = retweeted_status['user']['screen_name']
            retweeted_tweet_id = retweeted_status['id_str']
            return f'https://twitter.com/{retweeted_user_name}/status/{retweeted_tweet_id}'
        else:
            return None

    def get_user(self, obj):
        return {
            'added_date': obj.user.added_date,
            'deleted_count': obj.user.deleted_count,
            'avatar': obj.user.full_data['profile_image_url_https'],
            'bio': obj.user.full_data['description'],
            'screen_name': obj.user.full_data['name'],
            'user_name': obj.user.full_data['screen_name'],
            'verified': obj.user.full_data['verified'],
        }


class UserSerializer(serializers.ModelSerializer):
    '''Serializer for targeted users.'''
    screen_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('added_date', 'deleted_count', 'user_name', 'screen_name', 'avatar', 'bio', 'verified')

    def get_screen_name(self, obj):
        return obj.full_data['name']

    def get_user_name(self, obj):
        return obj.full_data['screen_name']

    def get_avatar(self, obj):
        return obj.full_data['profile_image_url_https']

    def get_bio(self, obj):
        return obj.full_data['description']

    def get_verified(self, obj):
        return obj.full_data['verified']
