from django.contrib import admin


from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path("login/", user_login, name="login"),
    path('', home, name="home"),
    path('logout/', user_logout, name='logout'),
    path('plans/', user_table, name='user_table'),
    path('pay/<slug:slug>/', plan_pay, name='plan_pay'),
    path('thank_you/', thank_you, name='thank_you'),
   path('subscription/status/', subscription_status, name='subscription_status'),
   path('create-news/', create_news, name='create_news'),
    path('news/<int:news_id>/', news_detail, name='news_detail'),    
    path('send-mail/', send_test_email, name='send_mail'),
    path('search/', search_news, name='search_news'),
        path('videos/', news_video, name='news_video'),
        path('video_gallery/', video_gallery, name='video_gallery'),
        path('video/<int:video_id>/', video_detail, name='video_detail'),
        path('videos/', video_list, name='video_list'),
        path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('upload_video/', upload_video, name='upload_video'),
]


