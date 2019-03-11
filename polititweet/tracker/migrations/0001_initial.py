# Generated by Django 2.1.7 on 2019-03-11 01:31

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('tweet_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('full_data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('hibernated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('full_data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('added_date', models.DateTimeField(auto_now_add=True)),
                ('deleted_count', models.BigIntegerField(default=0)),
                ('flagged', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='tweet',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.User'),
        ),
    ]
