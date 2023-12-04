from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime

# Create your views here.
class PrivateFeedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PrivateFeed.objects.all().order_by('-date')
    serializer_class = PrivateFeedSerializer

class PublicFeedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PublicFeed.objects.all().order_by('-date')
    serializer_class = PublicFeedSerializer

class PrivateFeedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        PrivateFeeds = PrivateFeed.objects.filter(user=self.request.user).filter(date = datetime.today().date())
        serializer_context = {'request': request,}
        serializer_class = PrivateFeedSerializer(PrivateFeeds, many=True, context=serializer_context)
        return Response(serializer_class.data)