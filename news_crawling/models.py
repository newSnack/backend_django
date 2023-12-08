from django.db import models
from newSnack import settings


class News(models.Model):
    # 유저와의 관계를 foreign key로 추가함
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='news',
        null=True,  # 프라이빗은 True, 퍼블릭은 False (특정 유저와 연관관계가 있는가를 나타냄)
        blank=True,
        help_text="User for whom this news is personalized"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    org_link = models.URLField()
    link = models.URLField()
    pub_date = models.DateTimeField()
    content = models.TextField()

    def __str__(self):
        return self.title
