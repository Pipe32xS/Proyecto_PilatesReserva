# administrador/urls.py
from django.urls import path, include   # <-- añadimos include
from . import views
from . import views_perfiles

app_name = "administrador"

urlpatterns = [
    # Dashboard / Contactos
    path("", views.admin_home, name="home"),
    path("contactos/", views.listar_contactos, name="listar_contactos"),
    path("contactos/<int:contacto_id>/",
         views.modificar_contacto, name="modificar_contacto"),

    # Clases
    path("clases/", views.listar_clases, name="listar_clases"),
    path("clases/nueva/", views.crear_clase, name="crear_clase"),
    path("clases/<int:clase_id>/editar/",
         views.modificar_clase, name="modificar_clase"),
    path("clases/<int:clase_id>/eliminar/",
         views.eliminar_clase, name="eliminar_clase"),

    # Reservas (panel)
    path("reservas/", views.reservas_admin_list, name="reservas_list"),
    path("reservas/<int:reserva_id>/estado/",
         views.reserva_admin_cambiar_estado, name="reserva_cambiar_estado"),

    # Usuarios (panel)
    path("usuarios/", views.admin_usuarios_list, name="usuarios_list"),
    path("usuarios/nuevo/", views.admin_usuario_crear, name="usuario_crear"),
    path("usuarios/<int:user_id>/editar/",
         views.admin_usuario_editar, name="usuario_editar"),
    path("usuarios/<int:user_id>/toggle-activo/",
         views.admin_usuario_toggle_activo, name="usuario_toggle_activo"),

    # Horarios (CRUD completo)
    path("horarios/", views.horarios_list, name="horarios_list"),
    path("horarios/nuevo/", views.horario_crear, name="horario_crear"),
    path("horarios/<int:bloque_id>/editar/",
         views.horario_editar, name="horario_editar"),
    path("horarios/<int:bloque_id>/eliminar/",
         views.horario_eliminar, name="horario_eliminar"),
    path("horarios/generar-clases/", views.horarios_generar_clases,
         name="horarios_generar_clases"),

    # Perfiles (CRUD)  <-- NUEVO: incluye las rutas del módulo de perfiles
    path("perfiles/", include("administrador.urls_perfiles")),
    path("perfiles/<int:user_id>/reservas/",
         views_perfiles.perfil_reservas, name="perfil_reservas"),
    path("perfiles/<int:user_id>/reservas/",
         views_perfiles.perfil_reservas, name="perfil_reservas"),
    path("crm/", views.crm_contactos, name="crm_contactos"),
]
