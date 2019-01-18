from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('like', views.like, name='like'),
    path('unlike', views.unlike, name='unlike'),
    path('create', views.create, name='create'),
    path('finduser', views.find_user, name='find_user'),
    path('checkposts', views.check_posts, name='check_posts'),
    path('getrandompost', views.get_random_post, name='get_random_post'),
    path('deleteall', views.delete_all, name='delete_all'),
    path('getusers', views.get_users, name='get_users'),
    path('getposts', views.get_posts, name='get_posts'),
    path('getlikes', views.get_likes, name='get_likes')
]
