# index/tests/test_smoke_views.py
from django.test import TestCase
from django.urls import reverse


class IndexSmokeTests(TestCase):
    def test_index_get(self):
        r = self.client.get(reverse("index"))
        self.assertEqual(r.status_code, 200)

    def test_clases_get(self):
        r = self.client.get(reverse("clases"))
        self.assertEqual(r.status_code, 200)

    def test_contacto_get(self):
        r = self.client.get(reverse("contacto_publico"))
        self.assertEqual(r.status_code, 200)

    def test_contacto_post_valido_redirige(self):
        # ⚠️ Usar exactamente el mismo nombre de campo definido en el modelo/Form: "correo_electronico"
        r = self.client.post(reverse("contacto_publico"), {
            "nombre": "Ana",
            "correo": "ana@test.com",
            "telefono": "111",
            "mensaje": "Hola!"
        })
        # Con datos válidos, debe redirigir a la página de éxito
        self.assertIn(r.status_code, (302, 303))

    def test_contacto_post_invalido_no_redirige(self):
        # Email inválido → el form no valida y vuelve a mostrar la página
        r = self.client.post(reverse("contacto_publico"), {
            "nombre": "Ana",
            "correo_electronico": "correo-malo",
            "telefono": "111",
            "mensaje": "Hola!"
        })
        self.assertEqual(r.status_code, 200)   # se queda en la misma página
        self.assertContains(r, "correo")       # el form muestra error

    def test_contacto_exito_get(self):
        r = self.client.get(reverse("contacto_exito"))
        self.assertEqual(r.status_code, 200)

    def test_clase_reformer_get(self):
        r = self.client.get(reverse("clase_reformer"))
        self.assertEqual(r.status_code, 200)

    def test_clase_mat_get(self):
        r = self.client.get(reverse("clase_mat"))
        self.assertEqual(r.status_code, 200)

    def test_clase_grupal_get(self):
        r = self.client.get(reverse("clase_grupal"))
        self.assertEqual(r.status_code, 200)
