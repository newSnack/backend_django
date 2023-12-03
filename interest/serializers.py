from rest_framework.serializers import ModelSerializer
from .models import *

class InterestSerializer(ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'