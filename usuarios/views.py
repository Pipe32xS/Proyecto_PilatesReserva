# usuarios/views.py
from datetime import datetime, date, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import now

from administrador.models import ClasePilates
from index.models import Reserva  # tu modelo de reservas público

# Alias opcional para agregaciones (si en algún entorno no existiera index.Reserva)
try:
    from index.models import Reserva as ReservaAgg
except Exception:
    from administrador.models import ReservaClase as ReservaAgg


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


def _first_existing_field(model, candidates):
    """Devuelve el primer nombre de campo que exista en el modelo."""
    names = {f.name for f in model._meta.get_fields()}
    for c in candidates:
        if c in names:
            return c
    return None


def _exclude_canceladas(qs):
    """
    Excluye reservas canceladas si el modelo tiene un campo de estado
    común como 'estado' / 'status' / 'state'.
    """
    estado_field = _first_existing_field(
        qs.model, ["estado", "status", "state"])
    if estado_field:
        try:
            return qs.exclude(**{f"{estado_field}__iexact": "cancelada"})
        except Exception:
            # Si hay valores distintos (p. ej. 'cancelled'), ajusta aquí si lo necesitas.
            pass
    return qs


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


# Entrada segura para "Nueva reserva": redirige a clases del admin
@login_required
def reservar_entry(request):
    return redirect("usuarios:clases_disponibles")


@login_required
def nueva_reserva(request):
    """
    Flujo manual (compatibilidad): tipo/fecha/hora fija.
    El flujo recomendado es reservar desde clases_disponibles.
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
                        tipo=tipo,
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
    r = get_object_or_404(Reserva, pk=pk, user=request.user)
    if r.estado == "Cancelada":
        messages.info(request, "Esta reserva ya estaba cancelada.")
    else:
        r.estado = "Cancelada"
        r.save(update_fields=["estado"])
        messages.success(request, "Tu reserva fue cancelada.")
    return redirect("usuarios:mis_reservas")


# ----------------------- NUEVA vista (tarjetas) -----------------------
@login_required
def clases_disponibles(request):
    """
    Lista de clases (formato tarjetas) con filtros y paginación.
    Renderiza: templates/index/clases_grid.html
    """
    q = (request.GET.get("q") or "").strip()
    desde = request.GET.get("desde") or ""
    hasta = request.GET.get("hasta") or ""

    # Base: clases futuras (>= hoy) por defecto
    qs = ClasePilates.objects.all().order_by("fecha", "horario")
    if desde:
        qs = qs.filter(fecha__gte=desde)
    else:
        qs = qs.filter(fecha__gte=now().date())

    if hasta:
        qs = qs.filter(fecha__lte=hasta)

    if q:
        qs = qs.filter(
            Q(nombre_clase__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(nombre_instructor__icontains=q)
        )

    # Conteo de reservas por clase (excluyendo canceladas si el modelo tiene campo de estado)
    reservas_qs = ReservaAgg.objects.all()
    reservas_qs = _exclude_canceladas(reservas_qs)

    reservas = reservas_qs.values("clase_id").annotate(cnt=Count("id"))
    reservas_por_clase = {r["clase_id"]: r["cnt"] for r in reservas}

    # Paginación (12 por página)
    paginator = Paginator(qs, 12)
    page = request.GET.get("page") or 1
    page_obj = paginator.get_page(page)  # tolerante a out-of-range

    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "desde": desde,
        "hasta": hasta,
        "reservas_por_clase": reservas_por_clase,
        "reserve_url_name": "usuarios:reservar_clase",  # nombre namespaced
    }
    return render(request, "index/clases_grid.html", context)


@login_required
def reservar_clase(request, clase_id: int):
    """
    Crea una Reserva enlazada a una ClasePilates del admin, si hay cupo.
    También rellena tipo/fecha/inicio para mantener compatibilidad.
    """
    c = get_object_or_404(ClasePilates, pk=clase_id)

    # Fecha no pasada
    if c.fecha < timezone.localdate():
        messages.error(
            request, "No es posible reservar una clase en el pasado.")
        return redirect("usuarios:clases_disponibles")

    # Verificación de cupo (excluyendo canceladas si corresponde)
    try:
        # si definiste un helper en tu modelo de reservas
        hay_cupo = Reserva.hay_cupo(c)
    except Exception:
        # Fallback: contar reservas no canceladas
        user_res_qs = Reserva.objects.filter(clase=c)
        user_res_qs = _exclude_canceladas(user_res_qs)
        reservados = user_res_qs.count()
        hay_cupo = reservados < (c.capacidad_maxima or 0)

    if not hay_cupo:
        messages.warning(request, "La clase ya no tiene cupos disponibles.")
        return redirect("usuarios:clases_disponibles")

    # Evitar duplicado por unique constraint (usuario + clase)
    ya_tiene_qs = Reserva.objects.filter(user=request.user, clase=c)
    ya_tiene_qs = _exclude_canceladas(ya_tiene_qs)
    if ya_tiene_qs.exists():
        messages.info(request, "Ya reservaste esta clase.")
        return redirect("usuarios:mis_reservas")

    # Crear la reserva
    Reserva.objects.create(
        user=request.user,
        clase=c,
        tipo=_infer_tipo_desde_nombre(c.nombre_clase),
        fecha=c.fecha,
        inicio=c.horario,
        fin=None,  # si quieres +1h, calcula y guarda
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
