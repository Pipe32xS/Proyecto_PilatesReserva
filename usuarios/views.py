# usuarios/views.py
from datetime import datetime, date, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from index.models import Reserva


# ----------------------- Helpers internos -----------------------
ALLOWED_MORNING = ["07:00", "08:00", "09:00", "10:00", "11:00", "12:30"]
ALLOWED_AFTERNOON = ["16:00", "17:00", "18:00", "19:00", "20:00"]
ALLOWED_ALL = set(ALLOWED_MORNING + ALLOWED_AFTERNOON)
ALLOWED_TYPES = {"reformer", "mat", "grupal"}


def _parse_time(hhmm: str) -> time:
    return datetime.strptime(hhmm, "%H:%M").time()


def _plus_one_hour(t: time) -> time:
    dt = datetime.combine(date.today(), t) + timedelta(hours=1)
    return dt.time()


def _is_mon_to_sat(d: date) -> bool:
    # Monday=0 ... Sunday=6
    return d.weekday() <= 5


# ----------------------- Vistas -----------------------
@login_required
def home_cliente(request):
    return render(request, "usuarios/cliente_home.html")


@login_required
def mis_reservas(request):
    qs = Reserva.objects.filter(user=request.user).order_by("fecha", "inicio")
    hoy = timezone.localdate()

    proximas = qs.filter(
        Q(fecha__gt=hoy) |
        Q(fecha=hoy, estado__in=["Confirmada", "Pendiente"])
    )
    historial = qs.exclude(id__in=proximas.values("id"))

    contexto = {
        "reservas_proximas": proximas,
        "reservas_historial": historial,
        "total_proximas": proximas.count(),
        "total_historial": historial.count(),
        "total_canceladas": qs.filter(estado="Cancelada").count(),
    }
    return render(request, "usuarios/mis_reservas.html", contexto)


@login_required
def nueva_reserva(request):
    """
    MVP: Form para elegir tipo de clase, fecha y una hora dentro de:
    Mañana: 07:00–12:30  |  Tarde: 16:00–20:00  (lunes a sábado)
    """
    if request.method == "POST":
        tipo = (request.POST.get("tipo") or "").lower().strip()
        fecha_str = (request.POST.get("fecha") or "").strip()
        hora_str = (request.POST.get("hora") or "").strip()

        # Validaciones simples
        error = None
        if tipo not in ALLOWED_TYPES:
            error = "Selecciona un tipo de clase válido."
        else:
            try:
                f = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                f = None
            if not f or not _is_mon_to_sat(f):
                error = "La fecha debe ser de lunes a sábado."
            elif hora_str not in ALLOWED_ALL:
                error = "Selecciona una hora válida."
            else:
                # Todo OK: crear la reserva (si no existe duplicada)
                t_inicio = _parse_time(hora_str)
                t_fin = _plus_one_hour(t_inicio)

                ya_existe = Reserva.objects.filter(
                    user=request.user, fecha=f, inicio=t_inicio
                ).exists()

                if ya_existe:
                    error = "Ya tienes una reserva en ese horario."
                else:
                    Reserva.objects.create(
                        user=request.user,
                        tipo=tipo,            # <-- se guarda lo que viene del select
                        fecha=f,
                        inicio=t_inicio,
                        fin=t_fin,
                        estado="Confirmada",
                    )
                    messages.success(request, "¡Reserva creada con éxito!")
                    return redirect("usuarios:mis_reservas")

        contexto = {
            "hoy": timezone.localdate().strftime("%Y-%m-%d"),
            "manana": ALLOWED_MORNING,
            "tarde": ALLOWED_AFTERNOON,
            "error": error,
            "tipo_sel": tipo,
            "fecha_sel": fecha_str,
            "hora_sel": hora_str,
        }
        return render(request, "usuarios/nueva_reserva.html", contexto)

    # GET
    contexto = {
        "hoy": timezone.localdate().strftime("%Y-%m-%d"),
        "manana": ALLOWED_MORNING,
        "tarde": ALLOWED_AFTERNOON,
    }
    return render(request, "usuarios/nueva_reserva.html", contexto)


@login_required
def reserva_detalle(request, pk: int):
    r = get_object_or_404(Reserva, pk=pk, user=request.user)
    return render(request, "usuarios/reserva_detalle.html", {"r": r})


@login_required
def reserva_cancelar(request, pk: int):
    """
    Cancela la reserva del usuario actual (MVP: vía GET).
    """
    r = get_object_or_404(Reserva, pk=pk, user=request.user)
    if r.estado == "Cancelada":
        messages.info(request, "Esta reserva ya estaba cancelada.")
    else:
        r.estado = "Cancelada"
        r.save(update_fields=["estado"])
        messages.success(request, "Tu reserva fue cancelada.")
    return redirect("usuarios:mis_reservas")
