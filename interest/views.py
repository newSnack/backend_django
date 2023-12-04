from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class InterestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer

class UserInterestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserInterest.objects.all()
    serializer_class = UserInterestSerializer

class UserInterestView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        userInterests = UserInterest.objects.filter(user=self.request.user)
        serializer_context = {'request': request,}
        serializer_class = UserInterestSerializer(userInterests, many=True, context=serializer_context)
        return Response(serializer_class.data)