# Generated by Django 3.1 on 2020-12-28 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_certified',
            field=models.BooleanField(default=False),
        ),
    ]
