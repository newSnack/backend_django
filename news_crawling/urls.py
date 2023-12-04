from django.urls import path
from .views import PersonalNewsListView

urlpatterns = [
    path('personal-news/', PersonalNewsListView.as_view(), name='news-list'),
]
