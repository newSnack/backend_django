from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username