from django.contrib import admin
from .models import *

class PrivateFeedAdmin(admin.ModelAdmin):
    list_display = [f.name for f in PrivateFeed._meta.fields]
    list_editable = ('comment','imgURL')
,
class PublicFeedAdmin(admin.ModelAdmin):
    list_display = [f.name for f in PublicFeed._meta.fields]

# Register your models here.
admin.site.register(PrivateFeed, PrivateFeedAdmin)
admin.site.register(PublicFeed, PublicFeedAdmin)