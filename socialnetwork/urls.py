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
    path('getrandompost', views.get_random_post, name='get_random_post')
]
