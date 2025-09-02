# index/tests/test_urls_smoke.py
from django.test import TestCase
from django.urls import reverse


class IndexURLsSmoke(TestCase):
    def test_public_gets_200(self):
        urls_200 = [
            "index",
            "clases",
            "clase_reformer",
            "clase_mat",
            "clase_grupal",
            "contacto_publico",
            "contacto_exito",
        ]
        for name in urls_200:
            with self.subTest(name=name):
                r = self.client.get(reverse(name))
                self.assertEqual(r.status_code, 200)

    def test_contacto_post_valido_redirige(self):
        r = self.client.post(reverse("contacto_publico"), {
            "nombre": "Ana",
            "correo": "ana@test.com",   # ← según tu forms.py
            "telefono": "111",
            "mensaje": "Hola!"
        })
        self.assertIn(r.status_code, (302, 303))

    def test_contacto_post_invalido_muestra_form(self):
        r = self.client.post(reverse("contacto_publico"), {
            "nombre": "Ana",
            "correo": "correo-malo",
            "telefono": "111",
            "mensaje": "Hola!"
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "correo")
