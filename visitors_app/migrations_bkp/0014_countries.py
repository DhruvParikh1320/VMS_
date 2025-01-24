# Generated by Django 5.0.7 on 2024-07-26 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitors_app', '0013_roles'),
    ]

    operations = [
        migrations.CreateModel(
            name='countries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shortname', models.CharField(max_length=3)),
                ('name', models.CharField(max_length=150)),
                ('phonecode', models.IntegerField()),
            ],
            options={
                'verbose_name': 'countries',
                'db_table': 'countries',
            },
        ),
    ]
