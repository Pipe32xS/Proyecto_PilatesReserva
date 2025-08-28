from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [
        ("cliente", "Cliente"),
        ("administrador", "Administrador"),
    ]
    # Default evita errores al crear usuarios/superusuarios sin definir rol explícito
    rol = models.CharField(max_length=20, choices=ROLES, default="cliente")
