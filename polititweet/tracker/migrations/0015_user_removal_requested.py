# Generated by Django 4.0.6 on 2022-07-20 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0014_tweet_deleted_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='removal_requested',
            field=models.BooleanField(default=False),
        ),
    ]