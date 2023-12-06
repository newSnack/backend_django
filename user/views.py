from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import IDCheckSerializer
from user.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework.views import APIView
from interest.models import *
from rest_framework import status
from feed.models import *
from feed.serializers import *
from django.http import Http404

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = DetailSerializer

class UserInitializeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        nickname = request.data["nickname"]
        birthYear = request.data["birthYear"]
        interest = request.data["interest"]
        kakaoIsLinked = request.data["kakaoIsLinked"]
        emailIsLinked = request.data["emailIsLinked"]
        kakaoAddress = request.data["kakaoAddress"]
        emailAddress = request.data["emailAddress"]
        frequency = request.data["frequency"]
        receptTime = request.data["receptTime"]

        user = User.objects.get(pk=self.request.user.pk)
        user.nickname = nickname
        user.birthYear = birthYear
        user.kakaoIsLinked = kakaoIsLinked
        user.emailIsLinked = emailIsLinked
        user.kakaoAddress = kakaoAddress
        user.emailAddress = emailAddress
        user.frequency = frequency
        user.receptTime = receptTime
        user.save()

        return Response({"detail": "User initialized successfully."}, status=status.HTTP_200_OK)

class UserLikedPrivateFeedsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        PrivateLikedFeeds = PrivateFeed.objects.filter(user=self.request.user).filter(likeOrDislike=1)
        serializer_context = {'request': request,}
        serializer_class = PrivateFeedSerializer(PrivateLikedFeeds, many=True, context=serializer_context)
        return Response(serializer_class.data)
    
class UserLikedPublicFeedsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        likelist = User.objects.prefetch_related('like').get(pk=self.request.user.pk).like.all()
        if likelist:
            serializer_context = {'request': request,}
            serializer_class = PublicFeedSerializer(likelist, many=True, context=serializer_context)
            return Response(serializer_class.data)
        else:
            raise Http404("PublicFeed does not exist")

class IDCheckView(RetrieveAPIView):
    queryset = None
    serializer_class = IDCheckSerializer
    permission_classes = (AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        # username = self.request.data['username']
        username = kwargs['id']
        try :
            instance = dict()
            User.objects.get(username=username)
            instance['is_unique'] = False
        except User.DoesNotExist:
            instance['is_unique'] = True

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserInterestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = User.objects.get(pk=request.user.pk)
        new_interest_keywords = request.data.get("new_interest_keywords", [])
        new_interest_embeddings = request.data.get("new_interest_embeddings", [])

        # 새로운 관심사 키워드 검증 및 추가(0자면 안되, 50자 초과시 첫 50자만 슬라이싱해 저장)
        for keyword in new_interest_keywords:
            if isinstance(keyword, str) and 0 < len(keyword):
                user.interest_keywords.append(keyword[:50])

        # 새로운 관심사 임베딩 벡터 검증 및 추가(2048차원인지 검증)
        for embedding in new_interest_embeddings:
            if isinstance(embedding, list) and len(embedding) == 2048:
                user.interest_embeddings.append(embedding)

        user.save()
        return Response({"detail": "User interests updated successfully."}, status=status.HTTP_200_OK)
