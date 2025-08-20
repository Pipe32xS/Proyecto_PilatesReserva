# index/views.py
from django.shortcuts import render, redirect
from .forms import ContactoPublicoForm

# Home (landing) – usa templates/index.html


def index(request):
    return render(request, "index.html")

# Clases (listado/horarios) – usa templates/clases.html


def clases(request):
    return render(request, "clases.html")

# Contacto - éxito – usa templates/contacto_exito.html


def contacto_exito(request):
    return render(request, "contacto_exito.html")

# Contacto - formulario público – usa templates/contacto_form.html


def contacto_publico(request):
    if request.method == "POST":
        form = ContactoPublicoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("contacto_exito")
    else:
        form = ContactoPublicoForm()
    return render(request, "contacto_form.html", {"form": form})

# Páginas estáticas de clases – usan templates/clase_reformer.html, etc.


def clase_reformer(request):
    return render(request, "clase_reformer.html")


def clase_mat(request):
    return render(request, "clase_mat.html")


def clase_grupal(request):
    return render(request, "clase_grupal.html")
