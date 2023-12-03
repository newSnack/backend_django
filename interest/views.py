from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class InterestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer