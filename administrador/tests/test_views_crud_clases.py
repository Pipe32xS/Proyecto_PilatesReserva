# administrador/tests/test_views_crud_clases.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from administrador.models import ClasePilates
from datetime import date, time
from unittest.mock import patch

User = get_user_model()


class CrudClasesTests(TestCase):
    def setUp(self):
        # Usuario logueado (no hace falta que sea superuser con el patch)
        User.objects.create_user(username="u", password="x")
        self.client.login(username="u", password="x")

    # --- CREAR ---
    @patch("administrador.views._solo_admin", return_value=True)
    def test_crear_clase_get(self, _mock):
        url = reverse("administrador:crear_clase")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    @patch("administrador.views._solo_admin", return_value=True)
    def test_crear_clase_post_valido(self, _mock):
        url = reverse("administrador:crear_clase")
        data = {
            "nombre_clase": "Reformer",
            "fecha": date(2025, 8, 1),
            "horario": time(10, 0),
            "capacidad_maxima": 8,
            "nombre_instructor": "Sofía",
            "descripcion": "Clase de prueba"
        }
        r = self.client.post(url, data)
        self.assertIn(r.status_code, (302, 303))
        self.assertEqual(ClasePilates.objects.count(), 1)

    # --- MODIFICAR ---
    @patch("administrador.views._solo_admin", return_value=True)
    def test_modificar_clase_get(self, _mock):
        c = ClasePilates.objects.create(
            nombre_clase="Mat",
            fecha=date(2025, 8, 1),
            horario=time(9, 0),
            capacidad_maxima=10,
            nombre_instructor="Ana",
            descripcion="."
        )
        url = reverse("administrador:modificar_clase", args=[c.id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    @patch("administrador.views._solo_admin", return_value=True)
    def test_modificar_clase_post(self, _mock):
        c = ClasePilates.objects.create(
            nombre_clase="Mat",
            fecha=date(2025, 8, 1),
            horario=time(9, 0),
            capacidad_maxima=10,
            nombre_instructor="Ana",
            descripcion="."
        )
        url = reverse("administrador:modificar_clase", args=[c.id])
        r = self.client.post(url, {
            "nombre_clase": "Mat Avanzado",
            "fecha": date(2025, 8, 1),
            "horario": time(9, 0),
            "capacidad_maxima": 12,
            "nombre_instructor": "Ana",
            "descripcion": "."
        })
        self.assertIn(r.status_code, (302, 303))
        c.refresh_from_db()
        self.assertEqual(c.capacidad_maxima, 12)

    # --- ELIMINAR ---
    @patch("administrador.views._solo_admin", return_value=True)
    def test_eliminar_clase_get(self, _mock):
        c = ClasePilates.objects.create(
            nombre_clase="Reformer",
            fecha=date(2025, 8, 2),
            horario=time(10, 0),
            capacidad_maxima=8,
            nombre_instructor="Sofía",
            descripcion="."
        )
        url = reverse("administrador:eliminar_clase", args=[c.id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    @patch("administrador.views._solo_admin", return_value=True)
    def test_eliminar_clase_post(self, _mock):
        c = ClasePilates.objects.create(
            nombre_clase="Mat",
            fecha=date(2025, 8, 1),
            horario=time(9, 0),
            capacidad_maxima=10,
            nombre_instructor="Ana",
            descripcion="."
        )
        url = reverse("administrador:eliminar_clase", args=[c.id])
        r = self.client.post(url)
        self.assertIn(r.status_code, (302, 303))
        self.assertFalse(ClasePilates.objects.filter(id=c.id).exists())
