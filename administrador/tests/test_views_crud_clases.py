from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from administrador.models import ClasePilates
from datetime import date, time

User = get_user_model()


class CrudClasesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="x")
        self.client.login(username="u", password="x")

    def test_crear_clase_post_valido(self):
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

    def test_modificar_clase_post(self):
        c = ClasePilates.objects.create(
            nombre_clase="Mat", fecha=date(2025, 8, 1), horario=time(9, 0),
            capacidad_maxima=10, nombre_instructor="Ana", descripcion="."
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

    def test_eliminar_clase_post(self):
        c = ClasePilates.objects.create(
            nombre_clase="Mat", fecha=date(2025, 8, 1), horario=time(9, 0),
            capacidad_maxima=10, nombre_instructor="Ana", descripcion="."
        )
        url = reverse("administrador:eliminar_clase", args=[c.id])
        r = self.client.post(url)
        self.assertIn(r.status_code, (302, 303))
        self.assertFalse(ClasePilates.objects.filter(id=c.id).exists())

    # --- NUEVOS (GET) ---
    def test_crear_clase_get(self):
        url = reverse("administrador:crear_clase")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_modificar_clase_get(self):
        c = ClasePilates.objects.create(
            nombre_clase="Mat", fecha=date(2025, 8, 1), horario=time(9, 0),
            capacidad_maxima=10, nombre_instructor="Ana", descripcion="."
        )
        url = reverse("administrador:modificar_clase", args=[c.id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_eliminar_clase_get(self):
        c = ClasePilates.objects.create(
            nombre_clase="Reformer", fecha=date(2025, 8, 2), horario=time(10, 0),
            capacidad_maxima=8, nombre_instructor="Sofía", descripcion="."
        )
        url = reverse("administrador:eliminar_clase", args=[c.id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
