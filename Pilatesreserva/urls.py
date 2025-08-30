# Pilatesreserva/urls.py
from django.contrib import admin
from django.urls import path, include
from index import views as index_views  # importamos las vistas públicas

urlpatterns = [
    path("admin/", admin.site.urls),

    # 🔹 Ruta directa al listado de clases en tarjetas (debe ir ANTES que otros includes con 'clases/')
    path("clases/disponibles/", index_views.clases_disponibles_cards,
         name="clases_disponibles"),

    # Rutas de las apps
    path("", include("index.urls")),  # landing, contacto, etc.
    path("usuarios/", include(("usuarios.urls", "usuarios"), namespace="usuarios")),
    path("login/", include(("login.urls", "login"), namespace="login")),
    path("administrador/", include(("administrador.urls",
         "administrador"), namespace="administrador")),
]
