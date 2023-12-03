from django.db import models

# Create your models here.
class Interest(models.Model):
    name = models.CharField(max_length=30, help_text="관심사 이름")
    def __str__(self):
        return self.name