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
    #  path('category/<int:cat_id>/', category_news_list, name='category_news'),
    # optional: slug version:
    # path('category/slug/<slug:slug>/', category_news_by_slug, name='category_news_by_slug'),
]

