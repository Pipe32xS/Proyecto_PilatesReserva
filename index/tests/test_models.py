from django.test import TestCase
from django.contrib.auth import get_user_model
from index.models import Reserva
from datetime import date, time

User = get_user_model()


class ReservaIndexModelTests(TestCase):
    def test_str_y_ordering(self):
        # Usuario para las reservas
        u = User.objects.create_user(username="u1", password="x")

        # Choices válidos según el modelo: reformer / mat / grupal
        r1 = Reserva.objects.create(
            user=u, tipo="mat", fecha=date(2025, 8, 1), inicio=time(10, 0)
        )
        r2 = Reserva.objects.create(
            user=u, tipo="mat", fecha=date(2025, 8, 2), inicio=time(9, 0)
        )

        # __str__ debe incluir tipo y fecha/hora
        s = str(r1)
        self.assertIn("mat", s)
        self.assertIn("2025-08-01", s)
        self.assertIn("10:00:00", s)

        # ordering = ["-fecha", "-inicio"]  -> primero la más nueva; si misma fecha, inicio más tarde primero
        # Aquí r2 tiene fecha 2025-08-02, así que debe ir primero
        self.assertEqual(list(Reserva.objects.all()), [r2, r1])
