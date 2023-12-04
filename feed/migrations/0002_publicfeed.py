# Generated by Django 4.1.5 on 2023-12-03 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicFeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='피드제목', max_length=30)),
                ('content', models.TextField(help_text='본문(원문요약)')),
                ('comment', models.TextField(help_text='댓글여론요약')),
                ('originalURL', models.CharField(help_text='원본링크', max_length=100)),
                ('dateTime', models.DateTimeField(auto_now_add=True, help_text='발행날짜')),
            ],
        ),
    ]