# administrador/tests/test_urls_admin_smoke.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from administrador.models import ClasePilates
from datetime import date, time
from unittest.mock import patch

User = get_user_model()


class AdminURLsSmoke(TestCase):
    def setUp(self):
        # Usuario logueado cualquiera; los permisos los forzamos con el patch
        self.user = User.objects.create_user(username="admin", password="x")
        self.client.login(username="admin", password="x")

    @patch("administrador.views._solo_admin", return_value=True)
    def test_admin_home_200(self, _mock):
        r = self.client.get(reverse("administrador:home"))
        self.assertEqual(r.status_code, 200)

    @patch("administrador.views._solo_admin", return_value=True)
    def test_listar_clases_200(self, _mock):
        r = self.client.get(reverse("administrador:listar_clases"))
        self.assertEqual(r.status_code, 200)

    @patch("administrador.views._solo_admin", return_value=True)
    def test_crear_clase_get_200(self, _mock):
        r = self.client.get(reverse("administrador:crear_clase"))
        self.assertEqual(r.status_code, 200)

    @patch("administrador.views._solo_admin", return_value=True)
    def test_crear_modificar_eliminar_flujo_basico(self, _mock):
        # Crear
        r = self.client.post(reverse("administrador:crear_clase"), {
            "nombre_clase": "Reformer",
            "fecha": date(2025, 8, 1),
            "horario": time(10, 0),
            "capacidad_maxima": 8,
            "nombre_instructor": "Sofía",
            "descripcion": "X",
        })
        self.assertIn(r.status_code, (302, 303))
        c = ClasePilates.objects.latest("id")

        # Modificar (GET y POST)
        r = self.client.get(
            reverse("administrador:modificar_clase", args=[c.id]))
        self.assertEqual(r.status_code, 200)
        r = self.client.post(reverse("administrador:modificar_clase", args=[c.id]), {
            "nombre_clase": "Reformer Avanzado",
            "fecha": date(2025, 8, 1),
            "horario": time(10, 0),
            "capacidad_maxima": 10,
            "nombre_instructor": "Sofía",
            "descripcion": "Y",
        })
        self.assertIn(r.status_code, (302, 303))

        # Eliminar (GET y POST)
        r = self.client.get(
            reverse("administrador:eliminar_clase", args=[c.id]))
        self.assertEqual(r.status_code, 200)
        r = self.client.post(
            reverse("administrador:eliminar_clase", args=[c.id]))
        self.assertIn(r.status_code, (302, 303))
        self.assertFalse(ClasePilates.objects.filter(id=c.id).exists())
