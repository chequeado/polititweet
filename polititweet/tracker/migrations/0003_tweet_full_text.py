# Generated by Django 2.1.7 on 2019-03-11 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_auto_20190311_0617'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='full_text',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=300, null=True),
        ),
    ]
