from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('private', PrivateFeedViewSet)
router.register('public', PublicFeedViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('private/list', PrivateFeedView.as_view()),
    path('public/list', PublicFeedView.as_view())
]