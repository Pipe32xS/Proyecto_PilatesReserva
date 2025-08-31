# administrador/urls_perfiles.py
from django.urls import path
from . import views_perfiles as views

# OJO: no hace falta app_name aquí porque ya estás dentro del namespace "administrador"
urlpatterns = [
    path("", views.perfiles_list, name="perfiles_list"),
    path("crear/", views.perfil_crear, name="perfil_crear"),
    path("<int:pk>/editar/", views.perfil_editar, name="perfil_editar"),
    path("<int:pk>/eliminar/", views.perfil_eliminar, name="perfil_eliminar"),
]
