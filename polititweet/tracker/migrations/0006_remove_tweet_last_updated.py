# Generated by Django 2.1.7 on 2019-03-09 20:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0005_tweet_hibernated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tweet',
            name='last_updated',
        ),
    ]
