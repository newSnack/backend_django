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

        for i_pk in interest:
            userInterest = UserInterest()
            userInterest.user = user
            userInterest.interest = Interest.objects.get(en_name=i_pk)
            userInterest.save()

        return Response({"detail":"user intialize done"})

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