# Generated by Django 5.0.7 on 2024-08-21 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitors_app', '0030_user_employee_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='access_area',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appointment',
            name='access_card_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
