from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from rest_framework.exceptions import ValidationError


# Create your models here.
class UserManager(BaseUserManager):

    def create_user(self, username, password, **kwargs):
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username=None, password=None, **extra_fields):
        superuser = self.create_user(
            username=username,
            password=password,
        )
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.is_active = True
        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(max_length=100, unique=True, null=False, blank=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # 추가정보
    nickname = models.CharField(max_length=10, null=True, blank=True, help_text="닉네임")
    birthYear = models.IntegerField(default=0, help_text="출생연도")
    kakaoIsLinked = models.BooleanField(default=False, help_text="카카오톡 수신여부")
    emailIsLinked = models.BooleanField(default=False, help_text="이메일 수신여부")
    kakaoAddress = models.CharField(max_length=20, null=True, blank=True, help_text="카카오톡 주소")
    emailAddress = models.CharField(max_length=20, null=True, blank=True, help_text="이메일 주소")
    frequency = models.IntegerField(default=0, help_text="수신횟수")
    receptTime = models.CharField(max_length=30, null=True, blank=True, help_text="수신 시간대")

    interest_keywords = models.JSONField(default=list, blank=True) # 관심사 클릭에 의해 추가되는 문자열 형식의 키워드들을 모아놓은 리스트
                                                                   # 한단어가 아닌 구나 문장일 수 있으며, 네이버 뉴스 api 검색어 생성에 활용할 예정
    interest_embeddings = models.JSONField(default=list, blank=True) # 관심사 클릭에 의해, 뉴스제목 원문에 기반해 생성한 임베딩 벡터들을 모아놓은 리스트
                                                                     # 벡터는 2048차원의 실수 벡터이며, 크롤링해온 기사 목록들과 내용 유사도 측정에 활용할 예정


    objects = UserManager()

    USERNAME_FIELD = 'username'