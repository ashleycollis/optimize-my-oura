from django.urls import path
from . import views


urlpatterns = [
    path("health/", views.health, name="health"),
    path("auth/oura/login/", views.oura_login, name="oura_login"),
    path("auth/oura/callback/", views.oura_callback, name="oura_callback"),
    path("oura/me/", views.oura_me, name="oura_me"),
]


