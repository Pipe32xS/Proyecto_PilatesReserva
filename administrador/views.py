# administrador/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from .models import ClasePilates
from .forms import ClasePilatesForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def _solo_admin(request):
    rol = getattr(request.user, "rol", "").lower(
    ) if request.user.is_authenticated else ""
    return rol == "administrador"


@login_required
def admin_home(request):
    if not _solo_admin(request):
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    return render(request, "administrador/home.html")


@login_required
def listar_contactos(request):
    if not _solo_admin(request):
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    return render(request, "administrador/contactos_list.html")


@login_required
def modificar_contacto(request, contacto_id):
    if not _solo_admin(request):
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    return render(request, "administrador/contacto_form.html", {"contacto_id": contacto_id})


@login_required
def listar_clases(request):
    clases = ClasePilates.objects.all()
    return render(request, 'clases/listar_clases.html', {'clases': clases})


@login_required
def crear_clase(request):
    if request.method == 'POST':
        form = ClasePilatesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clase creada exitosamente.')
            return redirect('administrador:listar_clases')
    else:
        form = ClasePilatesForm()
    return render(request, 'clases/crear_clase.html', {'form': form})


@login_required
def modificar_clase(request, clase_id):
    clase = get_object_or_404(ClasePilates, id=clase_id)
    if request.method == 'POST':
        form = ClasePilatesForm(request.POST, instance=clase)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clase modificada exitosamente.')
            return redirect('administrador:listar_clases')
    else:
        form = ClasePilatesForm(instance=clase)
    return render(request, 'clases/modificar_clase.html', {'form': form})


@login_required
def eliminar_clase(request, clase_id):
    clase = get_object_or_404(ClasePilates, id=clase_id)
    if request.method == 'POST':
        clase.delete()
        messages.success(request, 'Clase eliminada exitosamente.')
        return redirect('administrador:listar_clases')
    return render(request, 'clases/eliminar_clase.html', {'clase': clase})
