from django.db import models
from django.db.models.deletion import CASCADE
from user.models import *

# Create your models here.
class Interest(models.Model):
    name = models.CharField(max_length=30, help_text="관심사 이름")
    def __str__(self):
        return self.name
    
class UserInterest(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=CASCADE, help_text="유저")
    interest = models.ForeignKey(Interest, null=True, blank=True, on_delete=CASCADE, help_text="관심사")
    def __str__(self):
        return self.user.username + "-" + self.interest.name