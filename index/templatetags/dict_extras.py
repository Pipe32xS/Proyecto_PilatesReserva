from django import template

register = template.Library()


@register.filter
def get_item(d, key):
    """
    Accede a diccionario de forma segura: d[key] -> d.get(key, 0)
    """
    try:
        return d.get(key, 0)
    except Exception:
        return 0


@register.filter
def sub(value, arg):
    """
    Resta segura en templates: value - arg
    """
    try:
        return (value or 0) - (arg or 0)
    except Exception:
        return 0


@register.filter
def gt(value, arg):
    """
    Mayor que: devuelve True si value > arg
    """
    try:
        return (value or 0) > (arg or 0)
    except Exception:
        return False
