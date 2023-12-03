from rest_framework.serializers import ModelSerializer
from .models import *

class PrivateFeedSerializer(ModelSerializer):
    class Meta:
        model = PrivateFeed
        fields = '__all__'

class PublicFeedSerializer(ModelSerializer):
    class Meta:
        model = PublicFeed
        fields = '__all__'