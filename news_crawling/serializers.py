from rest_framework import serializers

class NewsSerializer(serializers.Serializer):
    cnt = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    org_link = serializers.CharField()
    link = serializers.CharField()
    pDate = serializers.CharField()
    content = serializers.CharField()
