from django.db import models
from django.db.models.deletion import CASCADE
from user.models import *
from interest.models import *


# Create your models here.
class PrivateFeed(models.Model):
    title = models.CharField(max_length=30, help_text="피드제목")
    content = models.TextField(help_text="본문(원문요약)")
    comment = models.TextField(help_text="댓글여론요약", null=True)
    originalURL = models.CharField(max_length=100, help_text="원본링크")
    date = models.DateField(auto_now_add=True, help_text="발행날짜")
    imgURL = models.ImageField(blank=True, null=True, verbose_name='image')
    category = models.CharField(max_length=50, default='정치', help_text="기사 카테고리")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=CASCADE, help_text="소유자")
    likeOrDislike = models.IntegerField(default=0, help_text="소유자-좋아요:1/싫어요:-1/없음:0")


class PublicFeed(models.Model):
    title = models.CharField(max_length=30, help_text="피드제목")
    content = models.TextField(help_text="본문(원문요약)")
    comment = models.TextField(help_text="댓글여론요약", null=True)
    originalURL = models.CharField(max_length=100, help_text="원본링크")
    date = models.DateField(auto_now_add=True, help_text="발행날짜")
    imgURL = models.ImageField(blank=True, null=True, verbose_name='image')
    # interest = models.ForeignKey(Interest, null=True, blank=True, on_delete=CASCADE, help_text="관심사")
    category = models.CharField(max_length=50, default='정치', help_text="기사 카테고리")
    liked_user = models.ManyToManyField(User, related_name='like', blank=True)
    disliked_user = models.ManyToManyField(User, related_name='dislike', blank=True)
