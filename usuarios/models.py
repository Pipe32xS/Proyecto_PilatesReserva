# usuarios/models.py
from django.conf import settings
from django.db import models


class Reserva(models.Model):
    TIPO_CHOICES = [
        ("Reformer", "Reformer"),
        ("Mat", "Mat"),
        ("Grupal", "Grupal"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservas"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha = models.DateField()
    inicio = models.TimeField()
    fin = models.TimeField(blank=True, null=True)  # opcional
    estado = models.CharField(max_length=20, default="Confirmada")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tipo", "fecha", "inicio"],
                name="uniq_reserva_usuario_tipo_fecha_hora",
            )
        ]

    def __str__(self):
        return f"{self.user} | {self.tipo} {self.fecha} {self.inicio}"
