from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    pub_date = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = ['title', 'description', 'org_link', 'link', 'pub_date', 'content']

    def get_pub_date(self, obj):
        return obj.pub_date.strftime('%Y-%m-%d %H:%M:%S') if obj.pub_date else None
