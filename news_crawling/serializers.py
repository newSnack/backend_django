from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import News

User = get_user_model()


class NewsSerializer(serializers.ModelSerializer):
    pub_date = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = ['title', 'description', 'org_link', 'link', 'pub_date', 'content', 'user_id']

    def get_pub_date(self, obj):
        return obj.pub_date.strftime('%Y-%m-%d %H:%M:%S') if obj.pub_date else None

    def get_user_id(self, obj):
        return obj.user.id if obj.user else None
