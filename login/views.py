# login/views.py
from django.contrib import messages
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegistroClienteForm


def login_view(request):
    """
    Inicia sesión y redirige por rol:
      - administrador  -> administrador:home
      - cliente/otros  -> usuarios:home_cliente
    """
    if request.method == "POST":
        # ⛔️ No pases 'request' como primer parámetro a tu LoginForm personalizado
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Detección de rol robusta
            rol = (getattr(user, "rol", "") or "").lower()
            if rol == "administrador" or user.is_superuser or user.is_staff:
                # Asegúrate de que esta URL exista
                return redirect("administrador:home")
            return redirect("usuarios:home_cliente")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()  # ⛔️ No pases 'request' aquí tampoco

    return render(request, "login/login.html", {"form": form})


def registro_cliente(request):
    """
    Registro de clientes (usa el template login/registro.html)
    """
    form = RegistroClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request, "¡Cuenta creada con éxito! Ahora puedes iniciar sesión.")
        # Asegúrate de que el name de la URL de login sea 'login'
        return redirect("login:login")

    return render(request, "login/registro.html", {"form": form})


@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    # Ajusta el nombre de la URL de tu home público
    return redirect("index")  # o 'index:home' si está namespaced
