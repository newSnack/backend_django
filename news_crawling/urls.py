# from django.urls import path
# from .views import PersonalNewsListView, PublicNewsFeedView
#
# urlpatterns = [
#     path('personal-news/', PersonalNewsListView.as_view(), name='personal-news-list'),
#     path('public-news/', PublicNewsFeedView.as_view(), name='public-news-feed'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('crawl-personal/', views.store_crawled_personal_article, name='crawl_personal'),
    path('crawl-public/', views.store_crawled_public_article, name='crawl_public'),
]