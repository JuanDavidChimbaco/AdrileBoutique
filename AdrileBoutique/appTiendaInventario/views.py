from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets

from .models import Usuario, Categoria, Producto

from .serializers import (
    LoginUsuarioSerializer,
    UsuarioSerializer,
    ProductoSerializer,
    CategoriaSerializer,
)

# Create your views here.

# ===[vistas templates]===


@login_required(login_url="index")
def inicio(request):
    return redirect("dashboard")


def index(request):
    return render(request,"index.html",{})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"].strip()
        password = request.POST["password"]
        remember_me = request.POST.get("remember_me")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(
                    0
                )  # La sesión expirará cuando se cierre el navegador
            return redirect("dashboard")
        else:
            # El inicio de sesión falló, muestra un mensaje de error
            error_message = "Nombre de usuario o contraseña incorrectos."
            return render(request, "index.html", {"error_message": error_message})
    return render(request, "index.html", locals())


@login_required(login_url="index")
def custom_logout(request):
    logout(request)
    return redirect("index")


@login_required(login_url="index")
def dashboard(request):
    return render(request, "inventario/dashboard.html")


@login_required(login_url="index")
def perfil_usuario(request):
    return render(request, "inventario/perfil.html", {})


def categorias(request):
    return render(request, "inventario/frmCategorias.html", {})


def productos(request):
    return render(request, "inventario/frmProductos.html", {})


def proveedores(request):
    return render(request, "inventario/frmProveedores.html", {})


def agregar_categoria(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]  # Nombre del campo coincide con el formulario
        imagen = request.FILES[
            "imagen"
        ]  # Utiliza 'request.FILES' para manejar archivos
        cat_padre = request.POST.get(
            "categoria_padre"
        )  # Asegúrate de obtener la categoría padre adecuadamente

        # Crea una nueva instancia de la categoría y guárdala en la base de datos
        categoria = Categoria(nombre=nombre, imagen=imagen, categoria_padre=cat_padre)
        categoria.save()

        return redirect(
            "categoria_list"
        )  # Redirige a la lista de categorías o a donde desees

    return render(
        request, "inventario/frmCategorias.html"
    )  # Renderiza la página con el formulario


def editar_categoria(request, categoria_id):
    if request.method == "POST":
        nombre = request.POST["nombre"]  # Nombre del campo coincide con el formulario

        try:
            categoria = Categoria.objects.get(pk=categoria_id)
            categoria.nombre = nombre
            categoria.save()
            return redirect(
                "categoria_list"
            )  # Redirige a la lista de categorías o a donde desees
        except Categoria.DoesNotExist:
            # Maneja la excepción si la categoría no existe
            pass

    return render(
        request, "inventario/frmCategorias.html"
    )  # Renderiza la página con el formulario


def eliminar_categoria(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]  # Nombre del campo coincide con el formulario
        # Puedes obtener otros campos del formulario de manera similar
        # Crea una nueva instancia de la categoría y guárdala en la base de datos
        categoria = Categoria(nombre=nombre)
        categoria.save()
        return redirect(
            "categoria_list"
        )  # Redirige a la lista de categorías o a donde desees
    return render(
        request, "inventario/frmCategorias.html"
    )  # Renderiza la página con el formulario


# from django.http import HttpResponse

# def eliminar_categoria(request, categoria_id):
#     if request.method == 'POST':
#         try:
#             categoria = Categoria.objects.get(pk=categoria_id)
#             categoria.delete()
#             return redirect('categoria_list')  # Redirige a la lista de categorías o a donde desees
#         except Categoria.DoesNotExist:
#             # Maneja la excepción si la categoría no existe
#             pass

#     return HttpResponse(status=400)  # Devuelve una respuesta de error (código 400) si la solicitud no es válida

# ===[Api]===


class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuariosSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
