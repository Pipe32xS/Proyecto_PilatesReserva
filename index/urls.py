# index/urls.py
from django.urls import path
from . import views
from .views_chat import chat_api

app_name = "index"

urlpatterns = [
    # Landing
    path("", views.index, name="index"),

    # Página de Clases (la que extiende base_index y muestra tabs)
    path("clases/", views.clases, name="clases"),

    # Contacto público (form y confirmación)
    path("contacto/", views.contacto_publico, name="contacto_publico"),
    path("contacto/exito/", views.contacto_exito, name="contacto_exito"),

    # Catálogo de clases en tarjetas
    path("clases/disponibles/", views.clases_disponibles_cards,
         name="clases_disponibles_cards"),

    # Catálogo en grid
    path("catalogo/", views.clases_grid, name="clases_grid"),
    path("api/chat/", chat_api, name="chat_api"),
]
