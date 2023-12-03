from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class PrivateFeedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PrivateFeed.objects.all().order_by('-dateTime')
    serializer_class = PrivateFeedSerializer

class PublicFeedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PublicFeed.objects.all().order_by('-dateTime')
    serializer_class = PublicFeedSerializer