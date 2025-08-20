from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AdminSmokeTests(TestCase):
    def test_listar_clases_redirige_si_no_autenticado(self):
        # Si no hay sesión → debe redirigir al login
        r = self.client.get(reverse("administrador:listar_clases"))
        self.assertIn(r.status_code, (302, 303))

    def test_listar_clases_200_si_autenticado(self):
        # Crear usuario normal y loguearlo
        u = User.objects.create_user(username="u", password="x")
        self.client.login(username="u", password="x")
        # Ahora debe devolver 200 (OK)
        r = self.client.get(reverse("administrador:listar_clases"))
        self.assertEqual(r.status_code, 200)
