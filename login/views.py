# login/views.py
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.shortcuts import render, redirect, resolve_url
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import LoginForm, RegistroClienteForm


def login_view(request):
    """
    Inicia sesión con usuario o email (tu backend ya lo permite).
    Redirige por rol:
      - administrador  -> administrador:admin-home
      - cliente (u otros) -> usuarios:home_cliente
    """
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            rol = (getattr(user, "rol", "") or "").lower()

            if rol == "administrador":
                # >>> AQUÍ estaba el problema: NO usar 'dashboard'
                return redirect("administrador:home")
            else:
                return redirect("usuarios:home_cliente")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm(request)

    return render(request, "login/login.html", {"form": form})


def registrar_cliente(request):
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, "Cuenta creada. Ya puedes iniciar sesión.")
            return redirect("login:login")
    else:
        form = RegistroClienteForm()
    return render(request, "login/registro_cliente.html", {"form": form})


@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("index")
