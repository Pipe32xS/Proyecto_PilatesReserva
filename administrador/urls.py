# administrador/urls.py
from django.urls import path
from . import views
from django.contrib import admin


app_name = "administrador"

urlpatterns = [
    path("dashboard/", views.admin_home, name="home"),
    path("contactos/", views.listar_contactos, name="listar_contactos"),
    path("contactos/modificar/<int:contacto_id>/",
         views.modificar_contacto, name="modificar_contacto"),
    path('clases/', views.listar_clases, name='listar_clases'),

    path('clases/crear/', views.crear_clase, name='crear_clase'),
    path('clases/modificar/<int:clase_id>/',
         views.modificar_clase, name='modificar_clase'),
    path('clases/eliminar/<int:clase_id>/',
         views.eliminar_clase, name='eliminar_clase'),

]
