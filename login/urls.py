# login/urls.py
from django.urls import path
# ⛔️ Ya no necesitamos importar LogoutView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views

app_name = "login"

urlpatterns = [
    # Login propio
    path("", views.login_view, name="login"),

    # Logout (POST) – usa TU vista
    path("logout/", views.logout_view, name="logout"),

    # Registro
    path("registro/", views.registro_cliente, name="registro_cliente"),

    # ----- Recuperar contraseña -----
    path(
        "password_reset/",
        PasswordResetView.as_view(
            template_name="login/password_reset_form.html",
            email_template_name="login/password_reset_email.html",
            subject_template_name="login/password_reset_subject.txt",
            success_url="/login/password_reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="login/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="login/password_reset_confirm.html",
            success_url="/login/reset/complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name="login/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
