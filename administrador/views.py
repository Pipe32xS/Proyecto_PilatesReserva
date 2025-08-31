# administrador/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date

from index.models import Contacto

from .forms import (
    ClasePilatesForm,
    ReservaEstadoForm,
    UsuarioAdminForm,
    UsuarioCrearForm,
    HorarioBloqueForm,
    GenerarClasesForm,
    ContactoAdminForm,
)
from .models import ClasePilates, HorarioBloque  # <- modelo de horarios

User = get_user_model()

# ===== Elegir el modelo de reservas correcto =====
USE_INDEX_RESERVA = False
try:
    # típicamente: user, clase, (estado|status|...)
    from index.models import Reserva as ReservaModel
    USE_INDEX_RESERVA = True
except Exception:
    # típicamente: cliente, clase, (estado|...)
    from .models import ReservaClase as ReservaModel
    USE_INDEX_RESERVA = False


# ---- Helpers de autorización ----
def _solo_admin(user) -> bool:
    return getattr(user, "rol", "").lower() == "administrador"


def _forbidden_if_not_admin(request):
    if not request.user.is_authenticated or not _solo_admin(request.user):
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    return None


def _has_field(model, name: str) -> bool:
    """Helper seguro para verificar si un modelo tiene un campo por nombre."""
    try:
        model._meta.get_field(name)
        return True
    except Exception:
        return False


# ---- DASHBOARD HOME (con KPIs reales) ----
@login_required
def admin_home(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    hoy = timezone.localdate()
    lunes = hoy - timedelta(days=hoy.weekday())
    domingo = lunes + timedelta(days=6)

    # ---- Contactos pendientes ----
    contactos_qs = Contacto.objects.all()
    if _has_field(Contacto, "estado_mensaje"):
        contactos_pendientes = contactos_qs.filter(
            estado_mensaje__iexact="pendiente"
        ).count()
    elif _has_field(Contacto, "estado_contacto"):
        contactos_pendientes = contactos_qs.filter(
            estado_contacto__iexact="pendiente"
        ).count()
    elif _has_field(Contacto, "estado"):
        contactos_pendientes = contactos_qs.filter(
            estado__iexact="pendiente").count()
    else:
        # MVP: si no hay campo de estado, mostramos el total como pendientes
        contactos_pendientes = contactos_qs.count()

    # ---- Reservas de HOY ----
    reservas_qs = ReservaModel.objects.all()
    reservas_hoy = 0
    if _has_field(ReservaModel, "fecha"):
        reservas_hoy = reservas_qs.filter(fecha=hoy).count()
    elif _has_field(ReservaModel, "fecha_reserva"):
        reservas_hoy = reservas_qs.filter(fecha_reserva=hoy).count()
    elif _has_field(ReservaModel, "clase") and _has_field(ClasePilates, "fecha"):
        try:
            reservas_hoy = reservas_qs.select_related("clase").filter(
                clase__fecha=hoy
            ).count()
        except Exception:
            reservas_hoy = 0

    # ---- Clases de esta semana ----
    clases_semana = ClasePilates.objects.filter(
        fecha__range=(lunes, domingo)
    ).count()

    # ---- Usuarios activos ----
    usuarios_activos = User.objects.filter(is_active=True).count()

    # ---- Próximas clases (top 5) ----
    proximas_clases = (
        ClasePilates.objects.filter(fecha__gte=hoy)
        .order_by("fecha", "horario")[:5]
    )

    # ---- Últimos contactos (top 5) ----
    if _has_field(Contacto, "fecha_envio"):
        ultimos_contactos = Contacto.objects.all().order_by(
            "-fecha_envio", "-id")[:5]
    else:
        ultimos_contactos = Contacto.objects.all().order_by("-id")[:5]

    contexto = {
        "admin_name": request.user.username,
        "contactos_pendientes": contactos_pendientes,
        "reservas_hoy": reservas_hoy,
        "clases_semana": clases_semana,
        "usuarios_activos": usuarios_activos,
        "proximas_clases": proximas_clases,
        "ultimos_contactos": ultimos_contactos,
    }
    return render(request, "administrador/home.html", contexto)


# ---- CRM: listado de contactos ----
@login_required
def listar_contactos(request):
    """CRM: listado de mensajes de contacto con búsqueda/filtro/paginación."""
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    q = (request.GET.get("q") or "").strip()
    estado = (request.GET.get("estado") or "todos").lower()

    qs = Contacto.objects.all().order_by("-fecha_envio")

    # Búsqueda: usa los NOMBRES DE CAMPO reales del modelo Contacto
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q)
            | Q(correo__icontains=q)      # tu modelo usa 'correo'
            | Q(telefono__icontains=q)
            | Q(mensaje__icontains=q)
            | Q(comentario__icontains=q)
        )

    # Filtro por estado si corresponde
    if estado in {"pendiente", "revisado", "respondido"} and _has_field(Contacto, "estado_mensaje"):
        qs = qs.filter(estado_mensaje=estado)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    return render(
        request,
        "administrador/contactos_list.html",
        {
            "page_obj": page_obj,
            "paginator": paginator,
            "q": q,
            "estado": estado,
            "estados": ["todos", "pendiente", "revisado", "respondido"],
        },
    )


@login_required
def modificar_contacto(request, contacto_id: int):
    """CRM: ver/actualizar un contacto (estado y comentario)."""
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    contacto = get_object_or_404(Contacto, pk=contacto_id)

    if request.method == "POST":
        form = ContactoAdminForm(
            request.POST, instance=contacto, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Contacto actualizado.")
            return redirect("administrador:listar_contactos")
        messages.error(request, "Revisa el formulario.")
    else:
        form = ContactoAdminForm(instance=contacto, user=request.user)

    return render(
        request,
        "administrador/contacto_form.html",
        {"form": form, "contacto": contacto},
    )


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
        messages.error(request, "Revisa el formulario.")
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
        messages.error(request, "Revisa el formulario.")
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


# ===== Utilidades para Reservas =====
def _field_exists(model, name: str) -> bool:
    return any(getattr(f, "name", None) == name for f in model._meta.get_fields())


def _first_existing_field(model, candidates):
    for name in candidates:
        if _field_exists(model, name):
            return name
    return None


# ---- Panel de Reservas con filtros/búsqueda/paginación ----
@login_required
def reservas_admin_list(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    qs = ReservaModel.objects.all().order_by("-id")

    # select_related seguro según el modelo elegido
    client_fk = "user" if USE_INDEX_RESERVA else "cliente"
    for rel in (client_fk, "clase"):
        if _field_exists(ReservaModel, rel):
            try:
                qs = qs.select_related(rel)
            except Exception:
                pass

    # ---- FILTRO POR CLIENTE ----
    cliente_id = request.GET.get("cliente")
    if cliente_id and _field_exists(ReservaModel, client_fk):
        qs = qs.filter(**{f"{client_fk}_id": cliente_id})

    # -------- Filtros por estado --------
    estado_field = _first_existing_field(
        ReservaModel, ["estado", "status", "estado_reserva"]
    )
    f = (request.GET.get("f") or "todas").lower()
    if estado_field and f in {"confirmada", "pendiente", "cancelada", "completada"}:
        qs = qs.filter(**{f"{estado_field}__iexact": f})

    # Búsqueda por cliente
    q = (request.GET.get("q") or "").strip()
    if q and _field_exists(ReservaModel, client_fk):
        qs = qs.filter(
            Q(**{f"{client_fk}__username__icontains": q})
            | Q(**{f"{client_fk}__first_name__icontains": q})
            | Q(**{f"{client_fk}__last_name__icontains": q})
        )

    # -------- Paginación --------
    page = request.GET.get("page") or 1
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(page)

    filters = [
        ("todas", "Todas"),
        ("confirmada", "Confirmada"),
        ("pendiente", "Pendiente"),
        ("cancelada", "Cancelada"),
        ("completada", "Completada"),
    ]

    contexto = {
        "reservas": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "use_index_reserva": USE_INDEX_RESERVA,
        "f": f,
        "q": q,
        "estado_field": estado_field,
        "filters": filters,
        "cliente_id": cliente_id,
    }
    return render(request, "administrador/reservas_list.html", contexto)


@login_required
def reserva_admin_cambiar_estado(request, reserva_id: int):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    reserva = get_object_or_404(ReservaModel, pk=reserva_id)

    if request.method == "POST":
        form = ReservaEstadoForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, "Estado de la reserva actualizado.")
            return redirect("administrador:reservas_list")
        messages.error(
            request, "No se pudo actualizar el estado. Revisa el formulario.")
    else:
        form = ReservaEstadoForm(instance=reserva)

    return render(
        request,
        "administrador/reserva_cambiar_estado.html",
        {"form": form, "reserva": reserva},
    )


# ---------------------------
# Administración de Usuarios
# ---------------------------
@login_required
def admin_usuarios_list(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    q = (request.GET.get("q") or "").strip()
    estado = (request.GET.get("estado") or "todos").lower()
    sort = (request.GET.get("sort") or "id").lower()
    direction = (request.GET.get("dir") or "asc").lower()

    allowed = {
        "id": "id",
        "username": "username",
        "nombre": "first_name",
        "email": "email",
        "rol": "rol" if hasattr(User, "rol") else None,
        "estado": "is_active",
    }
    sort_field = allowed.get(sort) or "id"
    if direction == "desc":
        sort_field = f"-{sort_field}"

    qs = User.objects.all()

    if q:
        qs = qs.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
        )
    if estado == "activos":
        qs = qs.filter(is_active=True)
    elif estado == "inactivos":
        qs = qs.filter(is_active=False)

    qs = qs.order_by(sort_field, "id")

    paginator = Paginator(qs, 10)
    page = request.GET.get("page") or 1
    page_obj = paginator.get_page(page)

    return render(
        request,
        "administrador/usuarios_list.html",
        {
            "usuarios": page_obj.object_list,
            "page_obj": page_obj,
            "q": q,
            "estado": estado,
            "sort": sort,
            "dir": direction,
            "tiene_rol": any(hasattr(u, "rol") for u in page_obj.object_list),
        },
    )


@login_required
def admin_usuario_crear(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    if request.method == "POST":
        form = UsuarioCrearForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect("administrador:usuarios_list")
        messages.error(request, "Revisa el formulario.")
    else:
        form = UsuarioCrearForm(initial={"is_active": True})

    return render(request, "administrador/usuario_form_crear.html", {"form": form})


@login_required
def admin_usuario_editar(request, user_id: int):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    usuario = get_object_or_404(User, pk=user_id)

    # 🚫 No permitir editar al superusuario
    if usuario.is_superuser:
        messages.error(request, "No está permitido editar al superusuario.")
        return redirect("administrador:usuarios_list")

    if request.method == "POST":
        form = UsuarioAdminForm(request.POST, instance=usuario)
        if form.is_valid():
            # Evitar autobloqueo cambiando is_active a False sobre sí mismo
            if usuario.pk == request.user.pk and not form.cleaned_data.get("is_active", True):
                messages.error(request, "No puedes desactivarte a ti mismo.")
            else:
                form.save()
                messages.success(request, "Usuario actualizado correctamente.")
                return redirect("administrador:usuarios_list")
        else:
            messages.error(request, "Revisa los datos del formulario.")
    else:
        form = UsuarioAdminForm(instance=usuario)

    return render(
        request,
        "administrador/usuario_form.html",
        {"form": form, "usuario": usuario},
    )


@login_required
def admin_usuario_toggle_activo(request, user_id: int):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    if request.method != "POST":
        return HttpResponseForbidden("Método no permitido.")

    usuario = get_object_or_404(User, pk=user_id)

    # 🚫 No permitir (des)activar al superusuario
    if usuario.is_superuser:
        messages.error(
            request, "No está permitido (des)activar al superusuario.")
        back = request.META.get(
            "HTTP_REFERER") or "administrador:usuarios_list"
        return redirect(back)

    # 🚫 No permitir desactivarse a sí mismo
    if usuario.pk == request.user.pk and usuario.is_active:
        messages.error(request, "No puedes desactivarte a ti mismo.")
        back = request.META.get(
            "HTTP_REFERER") or "administrador:usuarios_list"
        return redirect(back)

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])
    messages.success(
        request,
        f"Usuario {'activado' if usuario.is_active else 'desactivado'} correctamente.",
    )
    back = request.META.get("HTTP_REFERER") or "administrador:usuarios_list"
    return redirect(back)


# ---------------------------
# Gestión de Horarios (Bloques)
# ---------------------------
@login_required
def horarios_list(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    dias = [
        ("0", "Lunes"),
        ("1", "Martes"),
        ("2", "Miércoles"),
        ("3", "Jueves"),
        ("4", "Viernes"),
        ("5", "Sábado"),
        ("6", "Domingo"),
    ]

    q = (request.GET.get("q") or "").strip()
    dia = request.GET.get("dia", "")
    activos = request.GET.get("activos", "todos")

    qs = HorarioBloque.objects.all().order_by("dia_semana", "hora_inicio")

    if dia != "":
        try:
            qs = qs.filter(dia_semana=int(dia))
        except ValueError:
            pass

    if activos == "solo_activos":
        qs = qs.filter(activo=True)
    elif activos == "solo_inactivos":
        qs = qs.filter(activo=False)

    if q:
        qs = qs.filter(instructor__icontains=q)

    return render(
        request,
        "administrador/horarios_list.html",
        {"bloques": qs, "dias": dias, "q": q, "dia": dia, "activos": activos},
    )


@login_required
def horario_crear(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    if request.method == "POST":
        form = HorarioBloqueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Bloque horario creado.")
            return redirect("administrador:horarios_list")
        messages.error(request, "Revisa el formulario.")
    else:
        form = HorarioBloqueForm()

    return render(request, "administrador/horario_form.html", {"form": form, "modo": "crear"})


@login_required
def horario_editar(request, bloque_id: int):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    bloque = get_object_or_404(HorarioBloque, pk=bloque_id)

    if request.method == "POST":
        form = HorarioBloqueForm(request.POST, instance=bloque)
        if form.is_valid():
            form.save()
            messages.success(request, "Bloque horario actualizado.")
            return redirect("administrador:horarios_list")
        messages.error(request, "Revisa el formulario.")
    else:
        form = HorarioBloqueForm(instance=bloque)

    return render(
        request,
        "administrador/horario_form.html",
        {"form": form, "modo": "editar", "bloque": bloque},
    )


@login_required
def horario_eliminar(request, bloque_id: int):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    bloque = get_object_or_404(HorarioBloque, pk=bloque_id)

    if request.method == "POST":
        bloque.delete()
        messages.success(request, "Bloque horario eliminado.")
        return redirect("administrador:horarios_list")

    return render(request, "administrador/horario_confirm_delete.html", {"bloque": bloque})


@login_required
def horarios_generar_clases(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    default_desde = timezone.localdate()
    default_hasta = default_desde + timedelta(days=28)

    if request.method == "POST":
        form = GenerarClasesForm(request.POST)
        if form.is_valid():
            return _generar_clases_desde_bloques(request, form.cleaned_data)
        messages.error(request, "Revisa el formulario.")
    else:
        form = GenerarClasesForm(
            initial={
                "desde": default_desde,
                "hasta": default_hasta,
                "solo_activos": True,
                "ignorar_existentes": True,
                "nombre_clase": "Clase de Pilates",
            }
        )

    activos_count = HorarioBloque.objects.filter(activo=True).count()
    total_count = HorarioBloque.objects.count()

    return render(
        request,
        "administrador/horarios_generar_clases.html",
        {"form": form, "activos_count": activos_count, "total_count": total_count},
    )


def _generar_clases_desde_bloques(request, data):
    d_ini: date = data["desde"]
    d_fin: date = data["hasta"]
    solo_activos = data.get("solo_activos", True)
    ignorar_existentes = data.get("ignorar_existentes", True)
    nombre_clase = (data.get("nombre_clase") or "Clase de Pilates").strip()
    desc_form = (data.get("descripcion") or "").strip()

    bloques = HorarioBloque.objects.all()
    if solo_activos:
        bloques = bloques.filter(activo=True)

    created = 0
    skipped = 0

    cur = d_ini
    while cur <= d_fin:
        weekday = cur.weekday()
        for b in bloques.filter(dia_semana=weekday):
            exists = ClasePilates.objects.filter(
                fecha=cur,
                horario=b.hora_inicio,
                nombre_instructor=(b.instructor or "").strip(),
            ).exists()

            if exists and ignorar_existentes:
                skipped += 1
                continue

            if not exists:
                cp = ClasePilates(
                    nombre_clase=nombre_clase,
                    fecha=cur,
                    horario=b.hora_inicio,
                    capacidad_maxima=b.capacidad,
                    nombre_instructor=(b.instructor or "").strip(),
                    descripcion=desc_form
                    or f"Generada automáticamente desde bloque (instructor: {b.instructor or 'N/A'}).",
                )
                cp.save()
                created += 1
            else:
                skipped += 1
        cur += timedelta(days=1)

    messages.success(
        request,
        f"Generación finalizada. Clases creadas: {created}. Saltadas/Existentes: {skipped}.",
    )
    return redirect("administrador:listar_clases")


# ---- CRM Contactos rápido (si usas una vista simple en sidebar) ----
@login_required
def crm_contactos(request):
    if (resp := _forbidden_if_not_admin(request)) is not None:
        return resp

    contactos = Contacto.objects.all().order_by("-fecha_envio")
    return render(request, "administrador/crm_contactos.html", {"contactos": contactos})
