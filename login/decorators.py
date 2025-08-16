from django.shortcuts import redirect
from functools import wraps
from django.urls import reverse
from django.http import HttpResponseForbidden

def rol_requerido(rol_permitido):
    def decorador(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.rol == rol_permitido:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No estas autorizado a ver esta página.")
        return wrapper
    return decorador