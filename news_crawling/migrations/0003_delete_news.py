# Generated by Django 4.1.5 on 2023-12-10 07:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news_crawling', '0002_news_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='News',
        ),
    ]
