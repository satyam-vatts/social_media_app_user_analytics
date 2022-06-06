from django.urls import path
from Home import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('user_admin', views.user_admin, name='user_admin')
]