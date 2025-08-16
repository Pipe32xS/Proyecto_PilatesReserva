# usuarios/urls.py
from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path("inicio/", views.home_cliente, name="home_cliente"),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),
    path("reservar/", views.nueva_reserva, name="nueva_reserva"),
    path("mis-reservas/<int:pk>/", views.reserva_detalle, name="reserva_detalle"),
    path("mis-reservas/<int:pk>/cancelar/",
         views.reserva_cancelar, name="reserva_cancelar"),  # NUEVA
]
