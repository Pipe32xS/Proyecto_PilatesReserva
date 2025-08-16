from .models import Contacto, ClasePilates
from django import forms


class ClasePilatesForm(forms.ModelForm):
    class Meta:
        model = ClasePilates
        fields = ['nombre_clase', 'fecha', 'horario',
                  'capacidad_maxima', 'nombre_instructor', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }


class ContactoAdminForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['estado_mensaje', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Si no es administrador, deshabilitar todos los campos
        if not self.user or self.user.rol != 'administrador':
            for field in self.fields.values():
                field.disabled = True
