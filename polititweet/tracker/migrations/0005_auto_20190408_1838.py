# Generated by Django 2.1.7 on 2019-04-08 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0004_user_monitored"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tweet",
            name="full_text",
            field=models.CharField(
                blank=True, db_index=True, default=None, max_length=400, null=True
            ),
        ),
    ]
