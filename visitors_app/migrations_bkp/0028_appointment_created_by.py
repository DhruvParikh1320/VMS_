# Generated by Django 5.0.7 on 2024-08-08 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitors_app', '0027_appointment_check_in_time_appointment_check_out_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='created_by',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
