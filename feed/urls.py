from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('private', views.PrivateFeedViewSet)
router.register('public', views.PublicFeedViewSet)

urlpatterns = [
    path('', include(router.urls)),
]