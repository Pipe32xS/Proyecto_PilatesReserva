from django.urls import path
from . import views

app_name = "login"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("registro/", views.registro_cliente, name="registro_cliente"),
    path("logout/", views.logout_view, name="logout"),
]
