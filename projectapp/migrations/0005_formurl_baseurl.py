# Generated by Django 5.0.7 on 2024-08-02 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectapp', '0004_formurl_apikey'),
    ]

    operations = [
        migrations.AddField(
            model_name='formurl',
            name='baseurl',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
