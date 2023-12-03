from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import IDCheckSerializer
from user.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import *

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = DetailSerializer

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