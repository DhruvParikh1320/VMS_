# Generated by Django 5.0.7 on 2024-07-25 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitors_app', '0010_appointment_detail_appointment_visitors_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='user/document'),
        ),
    ]
