# Generated by Django 5.0.7 on 2024-08-21 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitors_app', '0032_alter_appointment_access_card_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='access_area',
        ),
        migrations.AlterField(
            model_name='appointment',
            name='access_card_id',
            field=models.CharField(max_length=200),
        ),
    ]
