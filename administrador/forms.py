# administrador/forms.py
from django import forms
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

# 👇 Contacto vive en la app "index"
from index.models import Contacto

from .models import ClasePilates, HorarioBloque, PerfilUsuario

User = get_user_model()

# =======================
#  Clases / Contacto / Reservas
# =======================

try:
    # Si existe la app index con reservas reales, úsala
    from index.models import Reserva as ReservaModel
except Exception:
    # Fallback local
    from .models import ReservaClase as ReservaModel


class ClasePilatesForm(forms.ModelForm):
    class Meta:
        model = ClasePilates
        fields = [
            "nombre_clase",
            "fecha",
            "horario",
            "capacidad_maxima",
            "nombre_instructor",
            "descripcion",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "horario": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "nombre_clase": forms.TextInput(attrs={"class": "form-control"}),
            "capacidad_maxima": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "nombre_instructor": forms.TextInput(attrs={"class": "form-control"}),
        }


def _model_has_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
        return True
    except Exception:
        return False


class ContactoAdminForm(forms.ModelForm):
    """
    Form dinámico: solo incluye los campos de gestión que existan en tu modelo Contacto.
    Admite, en este orden de prioridad:
      - "estado_mensaje", "comentario"
      - "estado", "notas", "nota", "estado_contacto"
    Si ninguno existe, la forma queda sin campos (solo lectura).
    """

    class Meta:
        model = Contacto
        fields: list[str] = []  # se completa en __init__

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Candidatos conocidos de campos de gestión
        candidates_in_order = [
            "estado_mensaje",
            "comentario",
            "estado",
            "notas",
            "nota",
            "estado_contacto",
        ]

        existing: list[str] = [
            n for n in candidates_in_order if _model_has_field(Contacto, n)]

        # Limpiar cualquier campo autogenerado por Django y reconstruir solo con los existentes
        self.fields.clear()
        for name in existing:
            # formfield() respeta choices, tipos, etc.
            formfield = Contacto._meta.get_field(name).formfield()
            if formfield is None:
                # Por si fuese no editable
                continue
            # Aplica estilo Bootstrap básico
            if hasattr(formfield.widget, "attrs"):
                css = formfield.widget.attrs.get("class", "")
                formfield.widget.attrs["class"] = (
                    css + " form-control").strip()
            self.fields[name] = formfield

        # Si no hay campos gestionables, la forma queda vacía (no rompe en .is_valid())
        self._meta.fields = list(self.fields.keys())

        # Si no es admin, todo deshabilitado
        if not self.user or getattr(self.user, "rol", "").lower() != "administrador":
            for field in self.fields.values():
                field.disabled = True


class ReservaEstadoForm(forms.ModelForm):
    """Selecciona dinámicamente el campo de 'estado' disponible en el modelo de reservas."""

    class Meta:
        model = ReservaModel
        fields = []  # dinámico

    estado_field_name: str | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        opts = self._meta.model._meta
        candidates = ["estado", "estado_reserva", "status", "situacion"]

        def _by_name():
            for name in candidates:
                try:
                    return name, opts.get_field(name)
                except Exception:
                    pass
            return None, None

        def _first_with_choices():
            for f in opts.get_fields():
                if isinstance(f, models.Field) and getattr(f, "choices", None):
                    if isinstance(
                        f, (models.CharField, models.IntegerField,
                            models.SmallIntegerField)
                    ):
                        return f.name, f
            return None, None

        def _safe_char():
            for f in opts.get_fields():
                if isinstance(f, models.CharField) and getattr(f, "editable", True):
                    return f.name, f
            return None, None

        name, field = _by_name()
        if not name:
            name, field = _first_with_choices()
        if not name:
            name, field = _safe_char()

        if not name or not field:
            self.fields["__estado__"] = forms.CharField(
                required=False,
                label="Estado (no detectado)",
                help_text="No se detectó el campo de estado en el modelo.",
                widget=forms.TextInput(attrs={"class": "form-control"}),
            )
            self._meta.fields = ["__estado__"]
            self.estado_field_name = None
            return

        formfield = field.formfield(
            widget=forms.Select(attrs={"class": "form-select form-select-sm"})
            if getattr(field, "choices", None)
            else None
        ) or forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
        self.fields[name] = formfield
        self._meta.fields = [name]
        self.estado_field_name = name


# =======================
#  Admin de Usuarios
# =======================


class UsuarioAdminForm(forms.ModelForm):
    rol = forms.CharField(required=False, label="Rol",
                          help_text="Ej: administrador / cliente")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "is_active"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_active"].widget = forms.CheckboxInput(
            attrs={"class": "form-check-input"})
        self.fields["is_active"].label = "Activo"
        if hasattr(self.instance, "rol"):
            self.fields["rol"].initial = getattr(self.instance, "rol") or ""
            self.fields["rol"].widget = forms.TextInput(
                attrs={"class": "form-control"})
        else:
            self.fields.pop("rol")

    def save(self, commit=True):
        user = super().save(commit=False)
        if "rol" in self.cleaned_data and hasattr(user, "rol"):
            user.rol = (self.cleaned_data.get("rol") or "").strip()
        if commit:
            user.save()
        return user


class UsuarioCrearForm(forms.ModelForm):
    """
    Crear usuario: username, nombre, email, rol y password opcional.
    Si no se ingresa password, se crea con password no usable.
    """

    rol = forms.CharField(required=False, label="Rol",
                          help_text="Ej: administrador / cliente")
    password1 = forms.CharField(
        required=False, widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Password"
    )
    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Repite password",
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1") or ""
        p2 = cleaned.get("password2") or ""
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        if "rol" in self.cleaned_data and hasattr(user, "rol"):
            user.rol = (self.cleaned_data.get("rol") or "").strip()

        p1 = self.cleaned_data.get("password1") or ""
        if p1:
            user.set_password(p1)
        else:
            user.set_unusable_password()

        if commit:
            user.save()
        return user


# =======================
#  Gestión de Horarios
# =======================


class HorarioBloqueForm(forms.ModelForm):
    class Meta:
        model = HorarioBloque
        fields = ["dia_semana", "hora_inicio", "hora_fin",
                  "instructor", "capacidad", "activo"]
        widgets = {
            "dia_semana": forms.Select(attrs={"class": "form-select"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "hora_fin": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "instructor": forms.TextInput(attrs={"class": "form-control", "placeholder": "Opcional"}),
            "capacidad": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned = super().clean()
        hi = cleaned.get("hora_inicio")
        hf = cleaned.get("hora_fin")
        if hi and hf and hf <= hi:
            self.add_error(
                "hora_fin", "La hora de fin debe ser mayor a la de inicio.")
        return cleaned


class GenerarClasesForm(forms.Form):
    """Formulario para crear clases a partir de bloques en un rango de fechas."""

    desde = forms.DateField(widget=forms.DateInput(
        attrs={"type": "date", "class": "form-control"}))
    hasta = forms.DateField(widget=forms.DateInput(
        attrs={"type": "date", "class": "form-control"}))
    solo_activos = forms.BooleanField(
        required=False,
        initial=True,
        label="Usar solo bloques activos",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    nombre_clase = forms.CharField(
        required=False, initial="Clase de Pilates", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    descripcion = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 2})
    )
    ignorar_existentes = forms.BooleanField(
        required=True,
        initial=True,
        label="No crear si ya existe una clase en el mismo día/hora/instructor",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def clean(self):
        cleaned = super().clean()
        d = cleaned.get("desde")
        h = cleaned.get("hasta")
        if d and h and h < d:
            raise forms.ValidationError(
                "La fecha 'hasta' debe ser mayor o igual a 'desde'.")
        return cleaned


# =======================
#  Administrar Perfiles (CRUD)
# =======================


class PerfilUsuarioForm(forms.ModelForm):
    """Formulario simple para el CRUD de PerfilUsuario."""

    usuario = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Usuario",
    )

    class Meta:
        model = PerfilUsuario
        fields = [
            "usuario",
            "primer_nombre",
            "apellido_paterno",
            "apellido_materno",
            "rut",
            "direccion",
            "telefono",
        ]
        widgets = {
            "primer_nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido_paterno": forms.TextInput(attrs={"class": "form-control"}),
            "apellido_materno": forms.TextInput(attrs={"class": "form-control"}),
            "rut": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
        }
