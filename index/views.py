# index/views.py
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.contrib import messages

from .forms import ContactoPublicoForm
from administrador.models import ClasePilates
from .models import Contacto  # <- Modelo de contactos

# Detecta automáticamente el modelo de reservas disponible
USE_INDEX_RESERVA = False
try:
    from index.models import Reserva as ReservaModel
    USE_INDEX_RESERVA = True
except Exception:
    from administrador.models import ReservaClase as ReservaModel


# -------- Landing / Páginas estáticas --------
def index(request):
    return render(request, "index.html")


def clases(request):
    return render(request, "clases.html")


def contacto_exito(request):
    return render(request, "contacto_exito.html")


# -------- NUEVO: contacto desde landing --------
def contacto_publico(request):
    """
    Procesa el formulario de contacto del landing page.
    Guarda en el modelo Contacto y redirige con mensaje de éxito.
    """
    if request.method == "POST":
        form = ContactoPublicoForm(request.POST)
        if form.is_valid():
            # Guardamos el contacto en DB
            form.save()
            messages.success(
                request, "Tu mensaje fue enviado con éxito. ¡Gracias por contactarnos!")
            return redirect("contacto_exito")
        else:
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = ContactoPublicoForm()

    return render(request, "contacto_form.html", {"form": form})


def clase_reformer(request):
    return render(request, "clase_reformer.html")


def clase_mat(request):
    return render(request, "clase_mat.html")


def clase_grupal(request):
    return render(request, "clase_grupal.html")


# -------- Listado (legacy que ya tenías) --------
def clases_disponibles_cards(request):
    q = (request.GET.get("q") or "").strip()
    desde = request.GET.get("desde") or ""
    hasta = request.GET.get("hasta") or ""

    qs = ClasePilates.objects.all().order_by("fecha", "horario")
    qs = qs.filter(fecha__gte=desde or now().date())
    if hasta:
        qs = qs.filter(fecha__lte=hasta)
    if q:
        qs = qs.filter(
            Q(nombre_clase__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(nombre_instructor__icontains=q)
        )

    reservado = (
        ReservaModel.objects.values("clase_id").annotate(cnt=Count("id"))
    )
    reservas_por_clase = {r["clase_id"]: r["cnt"] for r in reservado}

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    return render(request, "index/clases_grid.html", {
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "desde": desde,
        "hasta": hasta,
        "reservas_por_clase": reservas_por_clase,
        "reserve_url_name": "reservar_clase",
    })


# -------- NUEVO: catálogo en grid forzado --------
def clases_grid(request):
    """
    Vista nueva, en URL nueva, que siempre usa el template de tarjetas.
    """
    q = (request.GET.get("q") or "").strip()
    desde = request.GET.get("desde") or ""
    hasta = request.GET.get("hasta") or ""

    qs = ClasePilates.objects.all().order_by("fecha", "horario")
    qs = qs.filter(fecha__gte=desde or now().date())
    if hasta:
        qs = qs.filter(fecha__lte=hasta)
    if q:
        qs = qs.filter(
            Q(nombre_clase__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(nombre_instructor__icontains=q)
        )

    reservado = (
        ReservaModel.objects.values("clase_id").annotate(cnt=Count("id"))
    )
    reservas_por_clase = {r["clase_id"]: r["cnt"] for r in reservado}

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    return render(request, "index/clases_grid.html", {
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "desde": desde,
        "hasta": hasta,
        "reservas_por_clase": reservas_por_clase,
        "reserve_url_name": "reservar_clase",
    })
