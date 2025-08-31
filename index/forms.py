# index/forms.py
from django import forms
from .models import Contacto  # Usa el modelo Contacto de la app index


class ContactoPublicoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ["nombre", "correo", "telefono", "mensaje"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Tu nombre"}
            ),
            "correo": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Tu correo"}
            ),
            "telefono": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Tu teléfono"}
            ),
            "mensaje": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Escribe tu mensaje aquí",
                    "rows": 5,
                }
            ),
        }
