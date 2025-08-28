from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect

from .forms import ClasePilatesForm
from .models import ClasePilates


# ---- Helpers de autorización ----
def _solo_admin(user) -> bool:
    return getattr(user, "rol", "").lower() == "administrador"


def _forbidden_if_not_admin(request):
    if not request.user.is_authenticated or not _solo_admin(request.user):
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    return None


# ---- Vistas de panel ----
@login_required
def admin_home(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp
    return render(request, "administrador/home.html")


@login_required
def listar_contactos(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp
    return render(request, "administrador/contactos_list.html")


@login_required
def modificar_contacto(request, contacto_id: int):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp
    return render(request, "administrador/contacto_form.html", {"contacto_id": contacto_id})


# ---- CRUD de clases ----
@login_required
def listar_clases(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp
    clases = ClasePilates.objects.all()
    return render(request, "clases/listar_clases.html", {"clases": clases})


@login_required
def crear_clase(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp
    if request.method == "POST":
        form = ClasePilatesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Clase creada exitosamente.")
            return redirect("administrador:listar_clases")
    else:
        form = ClasePilatesForm()
    return render(request, "clases/crear_clase.html", {"form": form})


@login_required
def modificar_clase(request, clase_id: int):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp
    clase = get_object_or_404(ClasePilates, id=clase_id)
    if request.method == "POST":
        form = ClasePilatesForm(request.POST, instance=clase)
        if form.is_valid():
            form.save()
            messages.success(request, "Clase modificada exitosamente.")
            return redirect("administrador:listar_clases")
    else:
        form = ClasePilatesForm(instance=clase)
    return render(request, "clases/modificar_clase.html", {"form": form})


@login_required
def eliminar_clase(request, clase_id: int):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp
    clase = get_object_or_404(ClasePilates, id=clase_id)
    if request.method == "POST":
        clase.delete()
        messages.success(request, "Clase eliminada exitosamente.")
        return redirect("administrador:listar_clases")
    return render(request, "clases/eliminar_clase.html", {"clase": clase})
