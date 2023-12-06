from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from rest_framework import status

# Create your views here.
class PrivateFeedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PrivateFeed.objects.all().order_by('-date')
    serializer_class = PrivateFeedSerializer

class PublicFeedViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = PublicFeed.objects.all().order_by('-date')
    serializer_class = PublicFeedSerializer

class PrivateFeedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        PrivateFeeds = PrivateFeed.objects.filter(user=self.request.user).filter(date = datetime.today().date())
        serializer_context = {'request': request,}
        serializer_class = PrivateFeedSerializer(PrivateFeeds, many=True, context=serializer_context)
        return Response(serializer_class.data)
    
class PublicFeedView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        interest = request.GET.get('interest', None)
        PublicFeeds = PublicFeed.objects.filter(interest=interest).filter(date = datetime.today().date())
        serializer_context = {'request': request,}
        serializer_class = PublicFeedSerializer(PublicFeeds, many=True, context=serializer_context)
        return Response(serializer_class.data)
    
class PrivateFeedLikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        privateFeed = PrivateFeed.objects.get(pk=pk)
        if (self.request.user == privateFeed.user):
            likeOrDislike = request.data["likeOrDislike"]
            originLike = privateFeed.likeOrDislike
            if (originLike == 0):
                privateFeed.likeOrDislike = likeOrDislike
            elif (originLike == 1):
                if (likeOrDislike == 1): # 좋아요 취소
                    privateFeed.likeOrDislike = 0
                elif (likeOrDislike == -1): # 싫어요
                    privateFeed.likeOrDislike = -1
            elif (originLike == -1):
                if (likeOrDislike == 1): # 좋아요
                    privateFeed.likeOrDislike = 1
                elif (likeOrDislike == -1): # 싫어요 취소
                    privateFeed.likeOrDislike = 0
            privateFeed.save()
            return Response({'detail':'private feed like/dislike save success'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail':'not authorized'}, status=status.HTTP_400_BAD_REQUEST)

class PublicFeedLikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        publicFeed = PublicFeed.objects.get(pk=pk)
        likeOrDislike = request.data["likeOrDislike"]
        if self.request.user in publicFeed.liked_user.all(): # 이미 좋아요
            if likeOrDislike == 1: # 좋아요 취소
                publicFeed.liked_user.remove(self.request.user)
                publicFeed.save()
            elif likeOrDislike == -1: # 싫어요
                publicFeed.disliked_user.add(self.request.user)
                publicFeed.liked_user.remove(self.request.user)
                publicFeed.save()
        elif self.request.user in publicFeed.disliked_user.all(): # 이미 싫어요
            if likeOrDislike == 1: # 좋아요
                publicFeed.liked_user.add(self.request.user)
                publicFeed.disliked_user.remove(self.request.user)
                publicFeed.save()
            elif likeOrDislike == -1: # 싫어요 취소
                publicFeed.disliked_user.remove(self.request.user)
                publicFeed.save()
        else: # 아무것도 안누른상태
            if likeOrDislike == 1: # 좋아요
                publicFeed.liked_user.add(self.request.user)
                publicFeed.save()
            elif likeOrDislike == -1: # 싫어요
                publicFeed.disliked_user.add(self.request.user)
                publicFeed.save()
        return Response({'detail':'public feed like/dislike save success'}, status=status.HTTP_200_OK)