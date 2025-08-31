# administrador/views_perfiles.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django import forms
from django.urls import reverse

from .models import PerfilUsuario

User = get_user_model()


# --- Form sencillo para PerfilUsuario ---
class PerfilUsuarioForm(forms.ModelForm):
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
            "usuario": forms.Select(attrs={"class": "form-select"}),
            "primer_nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido_paterno": forms.TextInput(attrs={"class": "form-control"}),
            "apellido_materno": forms.TextInput(attrs={"class": "form-control"}),
            "rut": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo usuarios activos; si estás editando, incluye al actual
        qs = User.objects.filter(is_active=True)
        if self.instance and self.instance.pk:
            qs = qs | User.objects.filter(pk=self.instance.usuario_id)
        self.fields["usuario"].queryset = qs.distinct()


# --- Helpers ---
def _must_be_admin(request):
    rol = (getattr(request.user, "rol", "") or "").lower()
    if rol != "administrador":
        messages.error(
            request, "No tienes permiso para acceder a esta sección.")
        return False
    return True


def _first_existing_field(model, candidates):
    # (No lo usamos en este archivo ahora, pero lo dejamos por si luego lo necesitas)
    names = {f.name for f in model._meta.get_fields()}
    for c in candidates:
        if c in names:
            return c
    return None


# -------------------- CRUD Perfiles --------------------
@login_required
def perfiles_list(request):
    if not _must_be_admin(request):
        return redirect("administrador:home")

    perfiles = (
        PerfilUsuario.objects.select_related("usuario")
        .order_by("usuario__username")
    )
    return render(
        request,
        "administrador/perfiles/perfiles_list.html",
        {"perfiles": perfiles},
    )


@login_required
def perfil_crear(request):
    if not _must_be_admin(request):
        return redirect("administrador:home")

    if request.method == "POST":
        form = PerfilUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil creado correctamente.")
            return redirect("administrador:perfiles_list")
    else:
        form = PerfilUsuarioForm()

    return render(
        request,
        "administrador/perfiles/perfil_form.html",
        {"form": form, "modo": "crear"},
    )


@login_required
def perfil_editar(request, pk: int):
    if not _must_be_admin(request):
        return redirect("administrador:home")

    perfil = get_object_or_404(PerfilUsuario, pk=pk)

    if request.method == "POST":
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado.")
            return redirect("administrador:perfiles_list")
    else:
        form = PerfilUsuarioForm(instance=perfil)

    return render(
        request,
        "administrador/perfiles/perfil_form.html",
        {"form": form, "modo": "editar"},
    )


@login_required
def perfil_eliminar(request, pk: int):
    if not _must_be_admin(request):
        return redirect("administrador:home")

    perfil = get_object_or_404(PerfilUsuario, pk=pk)

    if request.method == "POST":
        perfil.delete()
        messages.success(request, "Perfil eliminado.")
        return redirect("administrador:perfiles_list")

    return render(
        request,
        "administrador/perfiles/perfil_confirm_delete.html",
        {"perfil": perfil},
    )


# -------------------- Reservas por cliente (redirige al panel general con filtro) --------------------
@login_required
def perfil_reservas(request, user_id: int):
    """
    Redirige al panel general de reservas filtrando por cliente (?cliente=<id>).
    Así reutilizas la misma UI de reservas y ves únicamente las del usuario.
    """
    if not _must_be_admin(request):
        return redirect("administrador:home")

    # Verificamos que el usuario exista (opcional pero recomendable)
    get_object_or_404(User, pk=user_id)

    url = f"{reverse('administrador:reservas_list')}?cliente={user_id}"
    return redirect(url)
