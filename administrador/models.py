# administrador/models.py
from django.db import models
from django.conf import settings


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    primer_nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    rut = models.CharField(max_length=12, unique=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.usuario.username} ({getattr(self.usuario, 'rol', 'sin-rol')})"


class ClasePilates(models.Model):
    nombre_clase = models.CharField(max_length=100)
    fecha = models.DateField()
    horario = models.TimeField()
    capacidad_maxima = models.PositiveIntegerField()
    nombre_instructor = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        ordering = ["-fecha", "horario"]

    def __str__(self):
        return f'{self.nombre_clase} - {self.fecha} {self.horario}'


class ReservaClase(models.Model):
    # related_name único para evitar conflictos
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservas_clase',
        related_query_name='reserva_clase'
    )
    clase = models.ForeignKey(ClasePilates, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    asistencia_confirmada = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha_reserva"]

    def __str__(self):
        username = getattr(self.cliente, 'username', str(self.cliente))
        return f'{username} - {self.clase.nombre_clase} ({self.fecha_reserva.date()})'


class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo_electronico = models.EmailField()
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado_mensaje = models.CharField(
        max_length=50,
        choices=[
            ('pendiente', 'Pendiente'),
            ('revisado', 'Revisado'),
            ('respondido', 'Respondido')
        ],
        default='pendiente'
    )
    telefono = models.CharField(max_length=20)
    comentario = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f'{self.nombre} - {self.estado_mensaje}'


# =========================
# Gestión de Horarios (MVP)
# =========================
class HorarioBloque(models.Model):
    class DiaSemana(models.IntegerChoices):
        LUNES = 0, "Lunes"
        MARTES = 1, "Martes"
        MIERCOLES = 2, "Miércoles"
        JUEVES = 3, "Jueves"
        VIERNES = 4, "Viernes"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"

    dia_semana = models.IntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    # String para no depender de otro modelo (MVP simple)
    instructor = models.CharField(
        max_length=100, blank=True, help_text="Opcional")
    capacidad = models.PositiveSmallIntegerField(default=10)
    activo = models.BooleanField(default=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("dia_semana", "hora_inicio")
        verbose_name = "Bloque horario"
        verbose_name_plural = "Bloques horarios"

    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.hora_inicio}–{self.hora_fin} ({self.instructor or 'sin instructor'})"

    def clean(self):
        # Validación básica de rango horario
        from django.core.exceptions import ValidationError
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError(
                "La hora de fin debe ser mayor a la hora de inicio.")
