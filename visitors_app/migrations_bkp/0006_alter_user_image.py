# Generated by Django 5.0.7 on 2024-07-22 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitors_app', '0005_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(upload_to='user'),
        ),
    ]
