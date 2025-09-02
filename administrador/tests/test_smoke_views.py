# administrador/tests/test_smoke_views.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch

User = get_user_model()


class AdminSmokeTests(TestCase):
    def test_listar_clases_redirige_si_no_autenticado(self):
        r = self.client.get(reverse("administrador:listar_clases"))
        self.assertIn(r.status_code, (302, 303))  # login_required

    @patch("administrador.views._solo_admin", return_value=True)
    def test_listar_clases_200_si_admin_autenticado(self, _mock):
        # basta con estar logueado; el patch simula permisos de admin
        User.objects.create_user(username="u", password="x")
        self.client.login(username="u", password="x")
        r = self.client.get(reverse("administrador:listar_clases"))
        self.assertEqual(r.status_code, 200)

    def test_dashboard_denegado_si_no_es_admin(self):
        User.objects.create_user(username="user", password="x")
        self.client.login(username="user", password="x")
        r = self.client.get(reverse("administrador:home"))
        self.assertEqual(r.status_code, 403)

    def test_dashboard_redirige_si_no_autenticado(self):
        r = self.client.get(reverse("administrador:home"))
        self.assertIn(r.status_code, (302, 303))
