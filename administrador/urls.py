from django.urls import path
from . import views

app_name = "administrador"

urlpatterns = [
    # Dashboard / Contactos
    path("dashboard/", views.admin_home, name="home"),
    path("contactos/", views.listar_contactos, name="listar_contactos"),
    path("contactos/<int:contacto_id>/",
         views.modificar_contacto, name="modificar_contacto"),

    # CRUD de clases
    path("clases/", views.listar_clases, name="listar_clases"),
    path("clases/nueva/", views.crear_clase, name="crear_clase"),
    path("clases/<int:clase_id>/editar/",
         views.modificar_clase, name="modificar_clase"),
    path("clases/<int:clase_id>/eliminar/",
         views.eliminar_clase, name="eliminar_clase"),

    # Reservas
    path("reservas/", views.reservas_admin_list, name="reservas_list"),
    path("reservas/<int:reserva_id>/estado/",
         views.reserva_admin_cambiar_estado, name="reserva_cambiar_estado"),

    # Usuarios
    path("usuarios/", views.admin_usuarios_list, name="usuarios_list"),
    path("usuarios/nuevo/", views.admin_usuario_crear, name="usuario_crear"),
    path("usuarios/<int:user_id>/editar/",
         views.admin_usuario_editar, name="usuario_editar"),
    path("usuarios/<int:user_id>/toggle-activo/",
         views.admin_usuario_toggle_activo, name="usuario_toggle_activo"),
]
