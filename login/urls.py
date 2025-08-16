# login/urls.py
from django.urls import path
from . import views

app_name = "login"

urlpatterns = [
    path("", views.login_view, name="login"),                 # /login/
    path("logout/", views.logout_view, name="logout"),        # /login/logout/
    path("registro/", views.registrar_cliente, name="registro-cliente"),
]
