from django.test import TestCase
from django.urls import reverse


class IndexViewsSmokeTests(TestCase):
    def test_index_get(self):
        r = self.client.get(reverse("index"))
        self.assertEqual(r.status_code, 200)

    def test_clases_get(self):
        r = self.client.get(reverse("clases"))
        self.assertEqual(r.status_code, 200)

    def test_contacto_get(self):
        r = self.client.get(reverse("contacto_publico"))
        self.assertEqual(r.status_code, 200)

    def test_contacto_post_valido_redirige_a_exito(self):
        r = self.client.post(reverse("contacto_publico"), {
            "nombre": "Ana",
            "correo_electronico": "ana@test.com",
            "telefono": "111",
            "mensaje": "Hola!"
        })
        # Debe redirigir a la página de éxito
        self.assertIn(r.status_code, (302, 303))
        # Si falla por NoReverseMatch, cambia en la vista:
        # return redirect("contacto_exito")  (sin namespace)
