# administrador/chat_kb.py
import re
import unicodedata
from difflib import SequenceMatcher

# --- Helpers de normalización ---


def norm(s: str) -> str:
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# --- Pequeña KB local (puedes editar libremente) ---
FAQ = [
    {
        "q": ["horario", "horarios", "a que hora", "agenda", "clases hoy", "clases mañana"],
        "a": (
            "Nuestros horarios varían por día e instructor. "
            "En general tenemos bloques temprano, medio día y tarde. "
            "Puedo orientarte si me dices día y franja que te acomoda."
        ),
        "kw": ["horario", "clase", "hoy", "mañana", "tarde", "temprano"]
    },
    {
        "q": ["dirección", "direccion", "como llegar", "ubicación", "estacionamiento"],
        "a": (
            "Estamos en <tu dirección>. Hay estacionamiento en la cuadra y cicloestacionamientos cercanos. "
            "Si vienes por primera vez, te sugerimos llegar 10 minutos antes."
        ),
        "kw": ["direccion", "ubicacion", "llegar", "estacionamiento"]
    },
    {
        "q": ["precios", "cuanto cuesta", "planes", "packs", "membresia", "valor"],
        "a": (
            "Clase suelta: $X. Packs con descuento y planes mensuales disponibles. "
            "¿Prefieres clase suelta o te interesa algún pack?"
        ),
        "kw": ["precio", "valor", "plan", "pack", "costo", "membresia"]
    },
    {
        "q": ["tipos de clases", "reformer", "mat", "full power", "nivel", "principiantes"],
        "a": (
            "Trabajamos con Reformer, Mat y clases enfocadas. Para principiantes, recomendamos un bloque guiado. "
            "¿Tienes alguna preferencia o limitación física a considerar?"
        ),
        "kw": ["reformer", "mat", "nivel", "principiante", "intermedio", "avanzado"]
    },
    {
        "q": ["politicas", "tardanza", "cancelacion", "cancelación", "reagendar", "reprogramar"],
        "a": (
            "Puedes reagendar con al menos 12 horas de anticipación según disponibilidad. "
            "Si llegas tarde, haremos lo posible por integrarte sin afectar la clase."
        ),
        "kw": ["politica", "tarde", "cancel", "reagendar", "reprogramar"]
    },
    {
        "q": ["contacto", "hablar", "humano", "telefono", "whatsapp"],
        "a": (
            "Claro, puedo derivarte. Déjame un nombre y un medio de contacto (teléfono o correo) y te escribe una persona del equipo."
        ),
        "kw": ["contacto", "telefono", "whatsapp", "humano", "asesor"]
    },
]

GENERIC_HELP = (
    "Puedo ayudarte con horarios, tipos de clase, precios y políticas. "
    "Si quieres reservar, dime día/franja preferida y nombre + un contacto."
)


def answer_with_kb(user_text: str) -> str:
    text = norm(user_text)
    if not text:
        return "¿En qué te ayudo?"

    # 1) Coincidencia por palabra clave
    for item in FAQ:
        if any(k in text for k in item["kw"]):
            return item["a"]

    # 2) Similaridad a preguntas frecuentes
    best_score, best_ans = 0.0, None
    for item in FAQ:
        for q in item["q"]:
            sc = similar(text, norm(q))
            if sc > best_score:
                best_score, best_ans = sc, item["a"]
    if best_score >= 0.60:
        return best_ans

    # 3) Fallback
    return GENERIC_HELP
