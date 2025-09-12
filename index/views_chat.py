# index/views_chat.py
import json
import re
import unicodedata
from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Leemos clases desde tu app administrador (modelo real)
from administrador.models import ClasePilates


# ---------------------------
# Utilidades de texto
# ---------------------------
def _norm(s: str) -> str:
    """Normaliza texto: minúsculas, sin tildes, sin signos, espacios simples."""
    s = (s or "").lower().strip()
    s = "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def _unique_titlecase(names):
    """Quita duplicados ignorando tildes/caso y devuelve capitalizados."""
    seen = set()
    out = []
    for n in names:
        n = (n or "").strip()
        if not n:
            continue
        key = _norm(n)
        if key and key not in seen:
            seen.add(key)
            out.append(n.title())
    return out


def _detect_clase_tipo(msg_norm: str):
    """Detecta si el usuario pide un tipo específico para filtrar horarios."""
    if "reformer" in msg_norm:
        return "reformer"
    if "mat" in msg_norm:
        return "mat"
    if "grupal" in msg_norm or "grupo" in msg_norm:
        return "grupal"
    return None


def _reply(text: str) -> JsonResponse:
    return JsonResponse({"reply": text})


# ---------------------------
# Respuestas con datos reales
# ---------------------------
def _tipos_de_clase() -> str:
    """
    1) Si hay CHATBOT_CLASS_TYPES en settings, usar esa lista (curada).
    2) Si no, leer desde BD: nombres de ClasePilates distintos, limpiar y mapear.
    """
    curated = getattr(settings, "CHATBOT_CLASS_TYPES", None)
    if curated:
        lst = [str(x).strip() for x in curated if str(x).strip()]
        if lst:
            return "Ofrecemos estas clases:\n" + "• " + "\n• ".join(lst)

    # Fall back: leer desde BD y normalizar
    hoy = timezone.localdate()
    raw_names = (
        ClasePilates.objects.filter(fecha__gte=hoy)
        .values_list("nombre_clase", flat=True)
        .distinct()
    )

    # Mapeo de sinónimos/higiene para nombres de BD a nombres bonitos
    nice_map = {
        "reformer": "Reformer",
        "mat": "Mat",
        "grupal": "Grupal",
        "grupo": "Grupal",
        "full power": "Full Power",
        "fullpower": "Full Power",
    }

    cleaned = []
    for n in raw_names:
        key = _norm(n)
        pretty = None
        for k, nice in nice_map.items():
            if k in key:
                pretty = nice
                break
        cleaned.append(pretty or (n or "Clase de Pilates"))

    cleaned = _unique_titlecase(cleaned)
    if not cleaned:
        return "Tenemos clases Mat, Reformer y grupales. ¿Cuál te interesa?"
    return "Ofrecemos estas clases:\n" + "• " + "\n• ".join(cleaned)


def _proximas_clases_msg(msg_norm: str, limit=8, dias=14) -> str:
    """
    Lista próximas clases. Si el usuario menciona 'reformer', 'mat' o 'grupal',
    filtra por ese tipo. Limita a los próximos 'dias' (por defecto 14).
    """
    hoy = timezone.localdate()
    hasta = hoy + timedelta(days=dias)

    qs = ClasePilates.objects.filter(fecha__gte=hoy, fecha__lte=hasta)
    tipo = _detect_clase_tipo(msg_norm)
    if tipo:
        qs = qs.filter(nombre_clase__icontains=tipo)

    qs = qs.order_by("fecha", "horario")[:limit]

    if not qs:
        if tipo:
            return f"No hay clases de {tipo.title()} en los próximos {dias} días. ¿Quieres otra modalidad?"
        return f"No hay clases publicadas en los próximos {dias} días. ¡Pronto habrá más!"

    filas = []
    for c in qs:
        f = c.fecha.strftime("%d-%m-%Y")
        h = c.horario.strftime("%H:%M") if getattr(c, "horario", None) else ""
        nombre = (c.nombre_clase or "Clase de Pilates").title()
        inst = (
            f" · Instructor/a: {c.nombre_instructor}"
            if getattr(c, "nombre_instructor", None)
            else ""
        )
        filas.append(f"{f} {h} — {nombre}{inst}")

    encabezado = f"Próximas clases de {tipo.title()}:\n" if tipo else "Próximas clases:\n"
    return encabezado + "\n".join("• " + x for x in filas)


# ---------------------------
# Endpoint del bot
# ---------------------------
@csrf_exempt  # el front ya envía CSRF; lo dejamos permisivo para evitar fricciones
@require_POST
def chat_api(request):
    """Bot sencillo con intenciones + datos reales desde la BD."""
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return _reply("No entendí el mensaje. ¿Puedes intentar de nuevo?")

    raw = (data.get("message") or "").strip()
    if not raw:
        return _reply("Escríbeme tu consulta y te ayudo 🙂")

    msg = _norm(raw)

    # ---- Saludo / ayuda general
    if any(k in msg for k in ["hola", "buenas", "buenos dias", "buenas tardes", "ayuda"]):
        return _reply(
            "¡Hola! 👋 Soy el asistente de PilatesReserva. "
            "Puedo ayudarte con *horarios*, *ubicación/dirección*, *tipos de clases*, "
            "*precios* y *cómo reservar*."
        )

    # ---- Ubicación / Dirección
    if any(k in msg for k in [
        "ubicacion", "ubicación", "direccion", "direccion exacta",
        "donde estan", "donde quedan"
    ]):
        address = getattr(settings, "CHATBOT_ADDRESS",
                          "Av. Ejemplo 1234, Santiago, Chile")
        map_url = getattr(settings, "CHATBOT_MAP_URL", "")
        txt = f"Estamos en {address}."
        if map_url:
            txt += f" Ver mapa: {map_url}"
        return _reply(txt)

    # ---- Tipos de clases
    if ("tipo" in msg and "clase" in msg) or "modalidad" in msg or "clases" in msg:
        return _reply(_tipos_de_clase())

    # ---- Horarios / Próximas clases (con filtro por tipo si el mensaje lo menciona)
    if any(k in msg for k in ["horario", "horarios", "agenda", "cuando", "cuándo"]):
        return _reply(_proximas_clases_msg(msg_norm=msg, limit=8, dias=14))

    # ---- Precios / Planes
    if any(k in msg for k in ["precio", "precios", "valores", "costo", "planes", "membresia", "membresía"]):
        prices_text = getattr(
            settings,
            "CHATBOT_PRICES",
            "Tenemos planes por clase y membresías mensuales. "
            "Escríbenos a contacto@pilatesreserva.cl para enviarte el detalle actualizado."
        )
        return _reply(prices_text)

    # ---- Cómo reservar
    if "reserv" in msg or "inscrib" in msg or "agendar" in msg:
        return _reply(
            "Para reservar, crea tu cuenta e inicia sesión. "
            "Luego ve a *Clases* y elige el horario que prefieras. "
            "Si necesitas ayuda te guiamos por WhatsApp."
        )

    # ---- Contacto
    if any(k in msg for k in ["telefono", "teléfono", "whatsapp", "contacto"]):
        phone = getattr(settings, "CHATBOT_PHONE", "+56 9 1234 5678")
        return _reply(f"Puedes escribirnos por WhatsApp al {phone} o al correo contacto@pilatesreserva.cl.")

    # ---- FAQ muy simple por palabras clave
    FAQ = {
        "metodo pago": "Aceptamos transferencia y tarjetas a través de link de pago.",
        "estacionamiento": "Contamos con estacionamiento en el edificio (según disponibilidad).",
        "duracion": "Cada clase dura 55 minutos aproximadamente.",
        "covid": "Mantenemos medidas de higiene y sanitización de equipos entre clases.",
    }
    for key, txt in FAQ.items():
        if all(w in msg for w in key.split()):
            return _reply(txt)

    # ---- Fallback
    return _reply(
        "Gracias por tu mensaje. Puedo ayudarte con *horarios*, *ubicación/dirección*, "
        "*tipos de clases*, *precios* y *cómo reservar*. "
        "Si prefieres, escríbenos a contacto@pilatesreserva.cl."
    )
