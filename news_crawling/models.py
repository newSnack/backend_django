from django.db import models


class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    org_link = models.URLField()
    link = models.URLField()
    pub_date = models.DateTimeField()
    content = models.TextField()

    def __str__(self):
        return self.title
