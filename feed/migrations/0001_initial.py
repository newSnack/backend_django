# Generated by Django 4.1.5 on 2023-12-10 05:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('interest', '__first__'),
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
                ('date', models.DateField(auto_now_add=True, help_text='발행날짜')),
                ('imgURL', models.ImageField(blank=True, null=True, upload_to='', verbose_name='image')),
                ('disliked_user', models.ManyToManyField(blank=True, related_name='dislike', to=settings.AUTH_USER_MODEL)),
                ('interest', models.ForeignKey(blank=True, help_text='관심사', null=True, on_delete=django.db.models.deletion.CASCADE, to='interest.interest')),
                ('liked_user', models.ManyToManyField(blank=True, related_name='like', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PrivateFeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='피드제목', max_length=30)),
                ('content', models.TextField(help_text='본문(원문요약)')),
                ('comment', models.TextField(help_text='댓글여론요약')),
                ('originalURL', models.CharField(help_text='원본링크', max_length=100)),
                ('date', models.DateField(auto_now_add=True, help_text='발행날짜')),
                ('imgURL', models.ImageField(blank=True, null=True, upload_to='', verbose_name='image')),
                ('likeOrDislike', models.IntegerField(default=0, help_text='소유자-좋아요:1/싫어요:-1/없음:0')),
                ('user', models.ForeignKey(blank=True, help_text='소유자', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
