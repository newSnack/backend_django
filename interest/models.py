from django.db import models
from django.db.models.deletion import CASCADE
from user.models import *

# Create your models here.
class Interest(models.Model):
    en_name = models.CharField(max_length=30, primary_key=True, help_text="관심사명(en)")
    ko_name = models.CharField(max_length=30, help_text="관심사명(ko)")
    
class UserInterest(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=CASCADE, help_text="유저")
    interest = models.ForeignKey(Interest, null=True, blank=True, on_delete=CASCADE, help_text="관심사")