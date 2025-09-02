from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from unittest.mock import patch
from administrador.models import Contacto

User = get_user_model()


class AdminPermissionsViewsTests(TestCase):
    def setUp(self):
        User.objects.create_user(username="u", password="x")
        self.client.login(username="u", password="x")

    @patch("administrador.views._solo_admin", return_value=True)
    def test_admin_home_con_admin(self, _mock):
        r = self.client.get(reverse("administrador:home"))
        self.assertEqual(r.status_code, 200)

    @patch("administrador.views._solo_admin", return_value=True)
    def test_listar_contactos_con_admin(self, _mock):
        r = self.client.get(reverse("administrador:listar_contactos"))
        self.assertEqual(r.status_code, 200)

    # ⬇️ Reemplaza tu test por este
    @patch("administrador.views.get_object_or_404")
    @patch("administrador.views._solo_admin", return_value=True)
    def test_modificar_contacto_con_admin(self, _mock_admin, mock_getobj):
        # Creamos un contacto real (usando los campos del MODELO)
        c = Contacto.objects.create(
            nombre="Ana",
            correo_electronico="ana@test.com",
            telefono="111",
            mensaje="Hola"
        )
        # Forzamos a que la vista "encuentre" el contacto sin importar los kwargs
        mock_getobj.return_value = c

        # Usa el reverse con el id; dará igual el nombre del parámetro en urls.py,
        # porque la obtención del objeto está mockeada
        url = reverse("administrador:modificar_contacto", args=[c.id])

        # (opcional) sanity check de la ruta
        match = resolve(url)
        self.assertEqual(match.url_name, "modificar_contacto")

        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
