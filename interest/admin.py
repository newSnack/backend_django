from django.contrib import admin
from .models import *

class InterestAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Interest._meta.fields]

class UserInterestAdmin(admin.ModelAdmin):
    list_display = [f.name for f in UserInterest._meta.fields]

# Register your models here.
admin.site.register(Interest, InterestAdmin)
admin.site.register(UserInterest, UserInterestAdmin)