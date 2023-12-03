from django.urls import path, include
from .views import IDCheckView
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register('list', UserViewSet) # 유저리스트 (테스트용)

urlpatterns = [
    path("", include(router.urls)),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj-rest-auth/checkid/<str:id>/', IDCheckView.as_view())
]