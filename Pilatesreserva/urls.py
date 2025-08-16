# Pilatesreserva/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("index.urls")),
    path("usuarios/", include(("usuarios.urls", "usuarios"), namespace="usuarios")),
    path("login/", include(("login.urls", "login"), namespace="login")),
    path("administrador/", include(("administrador.urls",
         "administrador"), namespace="administrador")),
]
