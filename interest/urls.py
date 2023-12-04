from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('basic', InterestViewSet)
router.register('user', UserInterestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('my_interest', UserInterestView.as_view())
]