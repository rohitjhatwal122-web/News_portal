from django.contrib import admin


from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path("login/", user_login, name="login"),
    path('home/', home, name="home"),
    path('logout/', user_logout, name='logout'),
    # path('news_detail/', news_detail, name='news_detail')
    
]
