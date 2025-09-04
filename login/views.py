# login/views.py
from django.contrib import messages
from django.contrib.auth import login, logout  # 👈 importa logout directamente
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, RegistroClienteForm


def login_view(request):
    """
    Inicia sesión y redirige por rol:
      - administrador  -> administrador:home
      - cliente/otros  -> usuarios:home_cliente
    """
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            rol = (getattr(user, "rol", "") or "").lower()
            if rol == "administrador" or user.is_superuser or user.is_staff:
                return redirect("administrador:home")
            return redirect("usuarios:home_cliente")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(request, "login/login.html", {"form": form})


def registro_cliente(request):
    form = RegistroClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request, "¡Cuenta creada con éxito! Ahora puedes iniciar sesión.")
        return redirect("login:login")
    return render(request, "login/registro.html", {"form": form})


@require_http_methods(["POST"])  # 👈 solo permite POST (evita 405 con GET)
def logout_view(request):
    logout(request)
    # Elige UNA de estas dos líneas y comenta la otra:
    return redirect("index:index")   # 👈 a landing
    # return redirect("login:login") # 👈 o de vuelta al login
