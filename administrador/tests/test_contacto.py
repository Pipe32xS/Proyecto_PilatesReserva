from django.test import TestCase
from administrador.models import Contacto


class ContactoModelTests(TestCase):
    def test_estado_por_defecto_es_pendiente(self):
        c = Contacto.objects.create(
            nombre="Juan",
            correo_electronico="juan@test.com",
            telefono="123456789",
            mensaje="Hola, consulta de prueba"
        )
        self.assertEqual(c.estado_mensaje, "pendiente")

    def test_str_incluye_nombre_y_estado(self):
        c = Contacto.objects.create(
            nombre="Ana",
            correo_electronico="ana@test.com",
            telefono="987654321",
            mensaje="Otra consulta"
        )
        s = str(c)
        self.assertIn("Ana", s)
        self.assertIn("pendiente", s)
