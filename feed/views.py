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
        PrivateFeeds = PrivateFeed.objects.filter(user=self.request.user).filter(date=datetime.today().date())
        serializer_context = {'request': request, }
        serializer_class = PrivateFeedSerializer(PrivateFeeds, many=True, context=serializer_context)
        return Response(serializer_class.data)


class PublicFeedView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        category_query = request.GET.get('category', None)

        if category_query:
            public_feeds = PublicFeed.objects.filter(category__icontains=category_query).filter(
                date=datetime.today().date())
        else:
            public_feeds = PublicFeed.objects.all()

        serializer_context = {'request': request, }
        serializer = PublicFeedSerializer(public_feeds, many=True, context=serializer_context)
        return Response(serializer.data)


class PrivateFeedLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        privateFeed = PrivateFeed.objects.get(pk=pk)
        user = self.request.user

        if user != privateFeed.user:
            return Response({'detail': 'not authorized'}, status=status.HTTP_400_BAD_REQUEST)

        likeOrDislike = request.data["likeOrDislike"]
        originLike = privateFeed.likeOrDislike

        # 사용자 관심사 키워드 리스트 업데이트
        if likeOrDislike == 1 and originLike != 1:  # 좋아요 또는 싫어요 -> 좋아요
            if privateFeed.title not in user.interest_keywords:
                if len(user.interest_keywords) >= 15:
                    user.interest_keywords.pop(0)  # 가장 오래된 항목 제거
                user.interest_keywords.append(privateFeed.title)
        elif originLike == 1:  # 좋아요 -> 싫어요 또는 좋아요 취소
            if privateFeed.title in user.interest_keywords:
                user.interest_keywords.remove(privateFeed.title)
        user.save()

        # privateFeed 좋아요 싫어요 업데이트
        if likeOrDislike != originLike:
            privateFeed.likeOrDislike = likeOrDislike
        else:  # 좋아요/싫어요 취소
            privateFeed.likeOrDislike = 0
        privateFeed.save()

        return Response({'detail': 'private feed like/dislike save success'}, status=status.HTTP_200_OK)


class PublicFeedLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        publicFeed = PublicFeed.objects.get(pk=pk)
        user = self.request.user
        likeOrDislike = request.data["likeOrDislike"]

        alreadyLiked = user in publicFeed.liked_user.all()
        alreadyDisliked = user in publicFeed.disliked_user.all()

        if likeOrDislike == 1:  # 좋아요 관련 처리
            if alreadyLiked:
                publicFeed.liked_user.remove(user)  # 좋아요 취소
                if publicFeed.title in user.interest_keywords:
                    user.interest_keywords.remove(publicFeed.title)
            else:
                if alreadyDisliked:
                    publicFeed.disliked_user.remove(user)  # 싫어요 -> 좋아요 전환
                if publicFeed.title not in user.interest_keywords:
                    if len(user.interest_keywords) >= 15:
                        user.interest_keywords.pop(0)  # 가장 오래된 항목 제거
                    user.interest_keywords.append(publicFeed.title)
                publicFeed.liked_user.add(user)  # 순수 좋아요 클릭
        elif likeOrDislike == -1:  # 싫어요 관련 처리
            if alreadyDisliked:
                publicFeed.disliked_user.remove(user)  # 싫어요 취소
            else:
                if alreadyLiked:
                    publicFeed.liked_user.remove(user)  # 좋아요 -> 싫어요 전환
                    if publicFeed.title in user.interest_keywords:
                        user.interest_keywords.remove(publicFeed.title)
                publicFeed.disliked_user.add(user)  # 순수 싫어요 클릭

        user.save()
        publicFeed.save()
        return Response({'detail': 'public feed like/dislike save success'}, status=status.HTTP_200_OK)