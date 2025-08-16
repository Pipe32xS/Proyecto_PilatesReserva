from django import forms
from administrador.models import Contacto


class ContactoPublicoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre', 'correo_electronico', 'telefono', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Tu correo'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu teléfono'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu mensaje aquí', 'rows': 5}),
        }
