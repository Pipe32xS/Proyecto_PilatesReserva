# index/urls.py
from django.urls import path
from . import views

app_name = None  # sin namespace para que {% url 'index' %} funcione tal cual

urlpatterns = [
    path("", views.index, name="index"),
    path("clases/", views.clases, name="clases"),
    path("contacto/", views.contacto_publico, name="contacto_publico"),
    path("contacto/exito/", views.contacto_exito, name="contacto_exito"),
    path("clases/reformer/", views.clase_reformer, name="clase_reformer"),
    path("clases/mat/", views.clase_mat, name="clase_mat"),
    path("clases/grupal/", views.clase_grupal, name="clase_grupal"),
    path("clases/disponibles/", views.clases_disponibles_cards,
         name="clases_disponibles"),

    # ---- NUEVA RUTA (grid) ----
    path("catalogo/", views.clases_grid, name="clases_grid"),
]
