# index/views.py
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.contrib import messages

from .forms import ContactoPublicoForm
from administrador.models import ClasePilates
from .models import Contacto  # Modelo de contactos (lo usa el form)

# Detecta automáticamente el modelo de reservas disponible
USE_INDEX_RESERVA = False
try:
    # Si tu proyecto define Reserva en index.models, úsala
    from index.models import Reserva as ReservaModel
    USE_INDEX_RESERVA = True
except Exception:
    # Si no existe, usa la de administrador como fallback
    from administrador.models import ReservaClase as ReservaModel


# -------- Landing / Páginas estáticas --------
def index(request):
    return render(request, "index.html")


def clases(request):
    """
    Vista única para clases.
    Puedes filtrar con ?tipo=reformer | mat | grupal
    """
    tipo = (request.GET.get("tipo") or "").lower().strip()
    context = {"tipo": tipo}
    return render(request, "clases.html", context)


def contacto_exito(request):
    return render(request, "contacto_exito.html")


# -------- Contacto desde landing --------
def contacto_publico(request):
    """
    Procesa el formulario de contacto del landing page.
    Guarda en el modelo Contacto y redirige con mensaje de éxito.
    """
    if request.method == "POST":
        form = ContactoPublicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Tu mensaje fue enviado con éxito. ¡Gracias por contactarnos!",
            )
            # Usa namespace para evitar conflictos
            return redirect("index:contacto_exito")
        else:
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = ContactoPublicoForm()

    return render(request, "contacto_form.html", {"form": form})


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

    reservado = ReservaModel.objects.values(
        "clase_id").annotate(cnt=Count("id"))
    reservas_por_clase = {r["clase_id"]: r["cnt"] for r in reservado}

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    return render(
        request,
        "index/clases_grid.html",
        {
            "page_obj": page_obj,
            "paginator": paginator,
            "q": q,
            "desde": desde,
            "hasta": hasta,
            "reservas_por_clase": reservas_por_clase,
            "reserve_url_name": "reservar_clase",
        },
    )


# -------- Catálogo en grid forzado --------
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

    reservado = ReservaModel.objects.values(
        "clase_id").annotate(cnt=Count("id"))
    reservas_por_clase = {r["clase_id"]: r["cnt"] for r in reservado}

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    return render(
        request,
        "index/clases_grid.html",
        {
            "page_obj": page_obj,
            "paginator": paginator,
            "q": q,
            "desde": desde,
            "hasta": hasta,
            "reservas_por_clase": reservas_por_clase,
            "reserve_url_name": "reservar_clase",
        },
    )


def faqs(request):
    return render(request, "index/faqs.html")


def novedades(request):
    posts = [
        {
            "title": "Nueva clase Reformer Intermedio",
            "excerpt": "Agregamos horario martes y jueves 19:30. Cupos limitados.",
            "tag": "Eventos",
            "date": "2025-09-01",
        },
        {
            "title": "Cómo activar el core en 3 pasos",
            "excerpt": "Mini-guía práctica para sentir el trabajo sin sobrecargar cuello ni zona lumbar.",
            "tag": "Consejos",
            "date": "2025-08-26",
        },
        {
            "title": "Promo de Primavera",
            "excerpt": "Plan Mat 2x/semana con 15% OFF durante septiembre.",
            "tag": "Promos",
            "date": "2025-09-10",
        },
    ]
    return render(request, "index/novedades.html", {"posts": posts})
