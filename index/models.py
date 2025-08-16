# index/models.py
from django.conf import settings
from django.db import models


class Reserva(models.Model):
    CLASES = [
        ("reformer", "Reformer"),
        ("mat", "Mat"),
        ("grupal", "Grupal"),
    ]
    ESTADOS = [
        ("Confirmada", "Confirmada"),
        ("Pendiente", "Pendiente"),
        ("Cancelada", "Cancelada"),
        ("Completada", "Completada"),
    ]

    # Acceso inverso único: user.reservas_index
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservas_index",         # <-- nombre único para la app index
        related_query_name="reserva_index",    # <-- nombre único para queries
    )

    tipo = models.CharField(max_length=20, choices=CLASES)
    fecha = models.DateField()
    inicio = models.TimeField()
    fin = models.TimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=12, choices=ESTADOS, default="Confirmada")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-inicio"]

    def __str__(self):
        return f"{self.user} - {self.tipo} - {self.fecha} {self.inicio}"
