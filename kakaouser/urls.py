from django.urls import path
from .views import *

urlpatterns = [
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/callback/<str:code>/', kakao_callback, name='kakao_callback'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),
    path('kakao/send-to-me/', send_to_me, name='send_to_me'),
]