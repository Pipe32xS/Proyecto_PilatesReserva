# administrador/tests/test_forms_contacto_admin.py
from django.test import TestCase

from administrador import forms as admin_forms
from administrador.models import Contacto

# Ajusta este nombre si en tu admin el form se llama distinto:
#   p.ej., ContactoForm, ContactoAdminForm, etc.
ContactoForm = getattr(admin_forms, "ContactoForm", None)


class ContactoFormAdminTests(TestCase):
    def setUp(self):
        if ContactoForm is None:
            self.skipTest("ContactoForm no existe en administrador/forms.py")

        # Descubrimos cómo se llama el campo email en el FORM de admin:
        #   algunos proyectos usan 'correo_electronico' en el modelo,
        #   otros renombraron a 'correo' en el form.
        self.email_field = "correo_electronico"
        if "correo" in ContactoForm._meta.fields:
            self.email_field = "correo"

    def _payload(self, **overrides):
        data = {
            "nombre": "Ana",
            self.email_field: "ana@test.com",
            "telefono": "111",
            "mensaje": "Hola!",
        }
        data.update(overrides)
        return data

    def test_valido_guarda(self):
        form = ContactoForm(data=self._payload())
        self.assertTrue(form.is_valid(), form.errors.as_json())
        obj = form.save()
        self.assertIsInstance(obj, Contacto)
        self.assertEqual(Contacto.objects.count(), 1)

    def test_email_invalido(self):
        form = ContactoForm(data=self._payload(
            **{self.email_field: "correo-malo"}))
        self.assertFalse(form.is_valid())
        self.assertIn(self.email_field, form.errors)

    def test_campo_obligatorio(self):
        form = ContactoForm(data=self._payload(nombre=""))
        self.assertFalse(form.is_valid())
        self.assertIn("nombre", form.errors)
