# Generated by Django 5.0.7 on 2024-08-14 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitors_app', '0029_user_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='employee_code',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
