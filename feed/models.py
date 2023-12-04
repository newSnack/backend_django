from django.db import models
from django.db.models.deletion import CASCADE
from user.models import *
from interest.models import *

# Create your models here.
class PrivateFeed(models.Model):
    title = models.CharField(max_length=30, help_text="피드제목")
    content = models.TextField(help_text="본문(원문요약)")
    comment = models.TextField(help_text="댓글여론요약")
    originalURL = models.CharField(max_length=100, help_text="원본링크")
    date = models.DateField(auto_now_add=True, help_text="발행날짜")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=CASCADE, help_text="소유자")
    
class PublicFeed(models.Model):
    title = models.CharField(max_length=30, help_text="피드제목")
    content = models.TextField(help_text="본문(원문요약)")
    comment = models.TextField(help_text="댓글여론요약")
    originalURL = models.CharField(max_length=100, help_text="원본링크")
    date = models.DateField(auto_now_add=True, help_text="발행날짜")
    interest = models.ForeignKey(Interest, null=True, blank=True, on_delete=CASCADE, help_text="관심사")