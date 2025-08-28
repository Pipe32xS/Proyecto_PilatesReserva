from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path("inicio/", views.home_cliente, name="home_cliente"),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),

    # 👉 'Nueva reserva' debe ir a la lista de clases del admin
    path("reservar/", views.reservar_entry, name="nueva_reserva"),

    path("mis-reservas/<int:pk>/", views.reserva_detalle, name="reserva_detalle"),
    path("mis-reservas/<int:pk>/cancelar/",
         views.reserva_cancelar, name="reserva_cancelar"),

    # --- Flujo nuevo conectado a clases creadas por admin ---
    path("clases-disponibles/", views.clases_disponibles,
         name="clases_disponibles"),
    path("clases/<int:clase_id>/reservar/",
         views.reservar_clase, name="reservar_clase"),

    # (opcional) mantener el flujo manual en una URL aparte
    path("reservar-manual/", views.nueva_reserva, name="reservar_manual"),
]
