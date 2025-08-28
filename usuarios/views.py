# usuarios/views.py
from datetime import datetime, date, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from administrador.models import ClasePilates
from index.models import Reserva


# ----------------------- Helpers internos existentes -----------------------
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


# ----------------------- Vistas originales (se mantienen) -----------------------
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


# --------- Entrada segura para "Nueva reserva" (redirige a clases del admin)
@login_required
def reservar_entry(request):
    """
    Entrada segura para 'Nueva reserva'. Redirige a la lista
    de clases creadas por el administrador.
    Si quieres mantener el flujo manual, queda disponible en /usuarios/reservar-manual/.
    """
    return redirect("usuarios:clases_disponibles")


@login_required
def nueva_reserva(request):
    """
    Flujo anterior (manual): tipo/fecha/hora fija. Lo mantenemos por compatibilidad.
    Ahora además tienes el nuevo flujo basado en clases del admin (reservar_entry -> clases_disponibles).
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
                        tipo=tipo,       # <-- se guarda lo que viene del select
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


# ----------------------- NUEVAS vistas conectadas a clases del admin -----------------------
@login_required
def clases_disponibles(request):
    """
    Lista SOLO las clases creadas por el administrador con fecha >= hoy,
    ordenadas por fecha y hora. Muestra cupos disponibles.
    """
    hoy = timezone.localdate()
    clases = ClasePilates.objects.filter(
        fecha__gte=hoy).order_by("fecha", "horario")

    items = []
    for c in clases:
        tomados = Reserva.cupos_tomados(c)
        libres = max(c.capacidad_maxima - tomados, 0)
        items.append({
            "obj": c,
            "cupos_tomados": tomados,
            "cupos_libres": libres,
            "hay_cupo": libres > 0,
            # si quieres mostrar badge "Vencida" en template, quedará False aquí
            "vencida": False,
        })
    return render(request, "usuarios/clases_disponibles.html", {"items": items})


@login_required
def reservar_clase(request, clase_id: int):
    """
    Crea una Reserva enlazada a una ClasePilates del admin, si hay cupo.
    También rellena tipo/fecha/inicio para mantener compatibilidad.
    """
    c = get_object_or_404(ClasePilates, pk=clase_id)

    # Verificación básica de fecha (no permitir pasado)
    if c.fecha < timezone.localdate():
        messages.error(
            request, "No es posible reservar una clase en el pasado.")
        return redirect("usuarios:clases_disponibles")

    # Verificación de cupo
    if not Reserva.hay_cupo(c):
        messages.warning(request, "La clase ya no tiene cupos disponibles.")
        return redirect("usuarios:clases_disponibles")

    # Evitar duplicado por unique constraint (usuario + clase)
    ya_tiene = Reserva.objects.filter(user=request.user, clase=c).exists()
    if ya_tiene:
        messages.info(request, "Ya reservaste esta clase.")
        return redirect("usuarios:mis_reservas")

    # Crear la reserva (llenando además los campos de compatibilidad)
    Reserva.objects.create(
        user=request.user,
        clase=c,
        tipo=_infer_tipo_desde_nombre(c.nombre_clase),
        fecha=c.fecha,
        inicio=c.horario,
        fin=None,  # opcional: calcular +1h si quieres
        estado="Confirmada",
    )
    messages.success(request, "¡Reserva creada con éxito!")
    return redirect("usuarios:mis_reservas")


# --- Helper para inferir 'tipo' desde el nombre de la clase del admin ---
def _infer_tipo_desde_nombre(nombre: str) -> str:
    nombre_l = (nombre or "").lower()
    if "reformer" in nombre_l:
        return "reformer"
    if "mat" in nombre_l:
        return "mat"
    if "grupal" in nombre_l:
        return "grupal"
    return "grupal"
