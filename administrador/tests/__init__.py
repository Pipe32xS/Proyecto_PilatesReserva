from django.test import TestCase
from administrador.models import ClasePilates
from datetime import date, time


class ClasePilatesModelTests(TestCase):
    def test_str(self):
        c = ClasePilates.objects.create(
            nombre_clase="Pilates Mat",
            fecha=date(2025, 8, 1),
            horario=time(10, 0),
            capacidad_maxima=12,
            nombre_instructor="Ana",
            descripcion="..."
        )
        self.assertIn("Pilates Mat", str(c))

    def test_ordering(self):
        a = ClasePilates.objects.create(
            nombre_clase="A", fecha=date(2025, 8, 1), horario=time(9, 0),
            capacidad_maxima=10, nombre_instructor="X", descripcion="."
        )
        b = ClasePilates.objects.create(
            nombre_clase="B", fecha=date(2025, 8, 2), horario=time(8, 0),
            capacidad_maxima=10, nombre_instructor="Y", descripcion="."
        )
        self.assertEqual(list(ClasePilates.objects.all()), [b, a])
