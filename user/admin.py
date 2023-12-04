from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = [f.name for f in User._meta.fields]

# Register your models here.
admin.site.register(User, UserAdmin)