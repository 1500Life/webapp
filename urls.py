from django.urls import path
from . import views

# from tweets.views import TweetsListView

urlpatterns = [
    path('', views.index, name='index'),
    path('show', views.show, name='show'),
    path('user_test', views.user_test, name='user_test'),
    path('user_info', views.user_info, name='user_info'),
    path('label', views.label, name='label'),
    path('api_user', views.api_user, name='api_user'),
    # path('archive', views.archive, name='archive'),
    path('tweets', views.tweets, name='tweets'),
    path('privacy-policy', views.privacy_policy, name='privacy-policy')
    # path('tweets-list', TweetsListView.as_view(), name='tweets-list'),
]