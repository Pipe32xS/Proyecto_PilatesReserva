from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch

User = get_user_model()


class AdminPermissionsViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="x")
        self.client.login(username="u", password="x")

    @patch("administrador.views._solo_admin", return_value=True)
    def test_admin_home_con_admin(self, _mock):
        r = self.client.get(reverse("administrador:home"))
        self.assertEqual(r.status_code, 200)

    @patch("administrador.views._solo_admin", return_value=True)
    def test_listar_contactos_con_admin(self, _mock):
        r = self.client.get(reverse("administrador:listar_contactos"))
        self.assertEqual(r.status_code, 200)

    @patch("administrador.views._solo_admin", return_value=True)
    def test_modificar_contacto_con_admin(self, _mock):
        r = self.client.get(
            reverse("administrador:modificar_contacto", args=[1]))
        # aunque el template use el ID, la vista actual solo renderiza con el id en contexto
        self.assertEqual(r.status_code, 200)
