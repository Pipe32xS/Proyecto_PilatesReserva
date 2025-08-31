# index/models.py
from django.conf import settings
from django.db import models
from administrador.models import ClasePilates  # <-- importamos la clase admin


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

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservas_index",
        related_query_name="reserva_index",
    )

    # --- NUEVO: vínculo (opcional por compatibilidad) ---
    clase = models.ForeignKey(
        ClasePilates,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservas_index",
    )

    # Campos existentes (se mantendrán para compatibilidad / reportes)
    tipo = models.CharField(max_length=20, choices=CLASES)
    fecha = models.DateField()
    inicio = models.TimeField()
    fin = models.TimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=12, choices=ESTADOS, default="Confirmada")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-inicio"]
        # Evita doble reserva del mismo usuario a misma clase
        constraints = [
            models.UniqueConstraint(
                fields=["user", "clase"], name="uniq_reserva_usuario_misma_clase"
            )
        ]

    def __str__(self):
        base = f"{self.user} - {self.tipo} - {self.fecha} {self.inicio}"
        if self.clase_id:
            base += f" (Clase: {self.clase.nombre_clase})"
        return base

    # --- Helpers de cupos ---
    @staticmethod
    def cupos_tomados(clase: ClasePilates) -> int:
        return Reserva.objects.filter(clase=clase).exclude(estado="Cancelada").count()

    @staticmethod
    def hay_cupo(clase: ClasePilates) -> bool:
        return Reserva.cupos_tomados(clase) < clase.capacidad_maxima

    from django.db import models


class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.correo}"
