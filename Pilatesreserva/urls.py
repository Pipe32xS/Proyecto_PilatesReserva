# Pilatesreserva/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Sitio público (landing, clases, contacto, etc.)
    path("", include(("index.urls", "index"), namespace="index")),

    # Módulos propios con namespace
    path("login/", include(("login.urls", "login"), namespace="login")),
    path("usuarios/", include(("usuarios.urls", "usuarios"), namespace="usuarios")),
    path("administrador/", include(("administrador.urls",
         "administrador"), namespace="administrador")),
]
