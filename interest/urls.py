from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('basic', views.InterestViewSet)
router.register('user', views.UserInterestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]