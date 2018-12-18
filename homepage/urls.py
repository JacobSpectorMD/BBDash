from django.conf.urls import url
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'labs1/', views.labs1, name="labs1"),
]
