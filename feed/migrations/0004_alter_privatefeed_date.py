# Generated by Django 4.1.5 on 2023-12-10 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0003_alter_privatefeed_comment_alter_privatefeed_imgurl_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privatefeed',
            name='date',
            field=models.CharField(help_text='발행날짜', max_length=100),
        ),
    ]