from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import Http404
from django.db import transaction
import os
import logging
logger = logging.getLogger(__name__)

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import (
    Usuario,
    Categoria,
    Proveedor,
    Producto,
    Cliente,
    Compra,
    DetalleCompra,
    Venta,
    DetalleVenta,
)
from .serializers import (
    UsuarioSerializer,
    CategoriaSerializer,
    ProveedorSerializer,
    ProductoSerializer,
    ClienteSerializer,
    CompraSerializer,
    DetalleCompraSerializer,
    VentaSerializer,
    DetalleVentaSerializer,
)

# Create your views here.


# ===[login y logout sin Api]=======================================================================0
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


# ===[vistas templates]===============================================================================
@login_required(login_url="index")
def inicio(request):
    return redirect("dashboard")


def index(request):
    return render(request, "index.html", {})


@login_required(login_url="index")
def dashboard(request):
    pertenece_a_administrador = request.user.groups.filter(name="administrador").exists()
    retorno = {"user": request.user, "es_administrador": pertenece_a_administrador}
    return render( request,"inventario/dashboard.html", retorno)


@login_required(login_url="index")
def perfil_usuario(request, usuario_id):
    print("ID del usuario logueado:", request.user.id)
    print("ID del usuario solicitado:", usuario_id)
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
        print("Usuario encontrado:", usuario)
    except Usuario.DoesNotExist:
        raise Http404("Usuario no encontrado")
    pertenece_a_administrador = request.user.groups.filter(name="administrador").exists()
    return render(
        request,
        "inventario/perfil.html",
        {"usuario": usuario, "es_administrador": pertenece_a_administrador},
    )

from django.db import Error, transaction

def modificarDatosUserPerfil(request,id):
    if request.method == "POST":
        try:
            nombres = request.POST["name"]
            apellidos = request.POST["last"]
            email = request.POST["email"]
            telefono = request.POST["phone"]
            direccion = request.POST["address"]
            usuario = request.POST["user"]
            foto = request.FILES.get("fileFoto", False)

            with transaction.atomic():
                user = Usuario().objects.get(pk=id)
                user.username=usuario
                user.first_name=nombres
                user.last_name=apellidos
                user.email=email
                user.telefono=telefono
                user.direccion=direccion
                if(foto):
                    if user.fotoPerfil == "":
                        user.fotoPerfil=foto
                    else:
                        os.remove('./media/'+str(user.fotoPerfil))
                        user.fotoPerfil=foto
                user.save()
                mensaje = "Datos Modificados Correctamente"
                retorno = {"mensaje": mensaje,"estado":True}

                return render(request, 'inventario/perfil.html',retorno)

        except Error as error:
            transaction.rollback()
            if 'user.username' in str(error):
                mensaje = "Ya existe un usuario con este nombre de usuario"
            elif 'user.email' in str(error):
                mensaje = "Ya existe un usuario con ese correo electronico"
            else:
                mensaje = error
        retorno = {"mensaje":mensaje,"estado":False}
        return render(request, 'inventario/perfil.html',retorno)


# def modificarDatosUserPerfil(request,id):
#     if request.method == "POST":
#         try:
#             nombres = request.POST["txtCedula"]
#             apellidos = request.POST["txtNombres"]
#             email = request.POST["txtApellido"]
#             telefono = request.POST["txtTelefono"]
#             direccion = request.POST["txtDireccion"]
#             foto = request.FILES.get("fileFoto", False)
#             username = request.POST["txtUserName"]
#             with transaction.atomic():
#                 user = Usuario().objects.get(pk=id)
#                 user.username=username
#                 user.first_name=nombres
#                 user.last_name=apellidos
#                 user.email=email
#                 user.telefono=telefono
#                 user.direccion=direccion
#                 user.userTelefono=telefono
#                 if(foto):
#                     if user.userFoto == "":
#                         user.userFoto=foto
#                     else:
#                         os.remove('./media/'+str(user.userFoto))
#                         user.userFoto=foto
#                 user.save()
#                 mensaje = "Datos Modificados Correctamente"
#                 retorno = {"mensaje": mensaje,"estado":True}
#                 if user.userTipo == "Administrador":
#                     return render(request, 'administrador/perfilUsuario.html',retorno)
#                 else:
#                     return render(request, 'asesor/perfilUsuario.html',retorno)
#         except Error as error:
#             transaction.rollback()
#             if 'username' in str(error):
#                 mensaje = "Ya existe un usuario con esta cedula"
#             elif 'user.username' in str(error):
#                 mensaje = "Ya existe un usuario con este nombre de usuario"
#             elif 'user.email' in str(error):
#                 mensaje = "Ya existe un usuario con ese correo electronico"
#             else:
#                 mensaje = error
#         retorno = {"mensaje":mensaje,"estado":False}
#         if user.userTipo == "Administrador":
#             return render(request, 'administrador/perfilUsuario.html',retorno)
#         else:
#             return render(request, 'asesor/perfilUsuario.html',retorno)
        

@login_required(login_url="index")
def categorias(request):
    return render(request, "inventario/frmCategorias.html", {})


@login_required(login_url="index")
def productos(request):
    proveedores = Proveedor.objects.all()
    categorias = Categoria.objects.all()
    return render(
        request,
        "inventario/frmProductos.html",
        {"proveedores": proveedores, "categorias": categorias},
    )


@login_required(login_url="index")
def proveedores(request):
    return render(request, "inventario/frmProveedores.html", {})


@login_required(login_url="index")
def clientes(request):
    return render(request, "inventario/frmClientes.html", {})


@login_required(login_url="index")
def entradas(request):
    proveedores = Proveedor.objects.all()
    productos = Producto.objects.all()
    return render(request, "inventario/frmEntrada.html", {"proveedores": proveedores, "productos": productos})


@login_required(login_url="index")
def salidas(request):
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()
    return render(request,"inventario/frmSalidas.html",{"clientes": clientes, "productos": productos})

# ===[Api]========================================================================================================
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    def create(self, request):
        # Obtener los datos de la solicitud
        proveedor_id = request.data.get('proveedor')
        detalles = request.data.get('detalles')  # Quita la lista de productos

        # Crear la compra
        compra = Compra.objects.create(proveedor_id=proveedor_id)

        for detalle_data in detalles:
            producto_id = detalle_data['producto']
            cantidad = detalle_data['cantidad']
            precio_unitario = detalle_data['precio_unitario']

            # Asociar el producto con la compra a través de DetalleCompra
            DetalleCompra.objects.create(compra=compra, producto_id=producto_id, cantidad=cantidad, precio_unitario=precio_unitario)

            # Actualizar la cantidad de stock del producto
            producto = Producto.objects.get(id=producto_id)
            producto.cantidad_stock += cantidad
            producto.save()

        # Actualizar la compra serializada
        serializer = CompraSerializer(compra)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DetalleCompraViewSet(viewsets.ModelViewSet):
    queryset = DetalleCompra.objects.all()
    serializer_class = DetalleCompraSerializer


class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

    def create(self, request):
        # Obtén los datos de la solicitud JSON
            cliente_id = request.data.get('cliente')
            detalles = request.data.get('detalles')

            # Crea la venta
            venta = Venta.objects.create(cliente_id=cliente_id)
            
            for detalle_data in detalles:
                producto_id = detalle_data.get('producto')
                cantidad = detalle_data.get('cantidad')
                precio_unitario = detalle_data.get('precio_unitario')

                # Asociar el producto con la venta a través de DetalleCompra
                DetalleVenta.objects.create(venta=venta, producto_id=producto_id, cantidad=cantidad, precio_unitario=precio_unitario)
                
                # Actualizar la cantidad de stock del producto
                producto = Producto.objects.get(id=producto_id)
                producto.cantidad_stock -= cantidad
                producto.save()

            serializer = VentaSerializer(venta)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer


# ===[otros metodos]============================================================================================
def productos_por_proveedor(request, proveedor_id):
    if request.method == "POST":
        if proveedor_id:
            # Filtra los productos relacionados con el proveedor
            productos = Producto.objects.filter(proveedor_id=proveedor_id).values(
                "id", "nombre"
            )  # Cambia 'nombre_producto' a 'nombre'
            # Convierte los datos a una lista de diccionarios
            productos_list = list(productos)
            return JsonResponse(productos_list, safe=False)
    # Si no se encontraron productos o hay un error, devuelve una respuesta de error
    return JsonResponse([], safe=False)
    
# =======================================================================================================================  
from django.db.models import Sum

def lista_compras(request):
    compras = Compra.objects.annotate(total_cantidad=Sum('detallecompra__cantidad'))
    return render(request, 'lista_compras.html', {'compras': compras})

@login_required(login_url="index")
def lista_ventas(request):
    ventas = Venta.objects.all()
    for venta in ventas:
        venta.total_cantidad = venta.detalleventa_set.aggregate(total_cantidad=Sum('cantidad'))['total_cantidad']
    return render(request, 'lista_ventas.html', {'ventas': ventas})

from django.http import JsonResponse

def cargar_productos(request):
    proveedor_id = request.GET.get('proveedor_id')
    productos = Producto.objects.filter(proveedor=proveedor_id).values('id', 'nombre')
    return JsonResponse(list(productos), safe=False)

# ===========================================================================================

from django.shortcuts import render
from .models import Producto

def lista_stock(request):
    productos = Producto.objects.all()
    return render(request, 'lista_stock.html', {'productos': productos})

from django.shortcuts import render
from .models import Venta, DetalleVenta
from django.db.models import Sum

def informe_ventas(request):
    ventas = Venta.objects.all()
    total_ventas = ventas.aggregate(total=Sum('detalleventa__cantidad'))

    return render(request, 'informe_ventas.html', {'ventas': ventas, 'total_ventas': total_ventas})

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'lista_productos.html', {'productos': productos})

from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductoForm
from .models import Producto

def agregar_producto(request, producto_id=None):
    if producto_id:
        producto = get_object_or_404(Producto, pk=producto_id)
    else:
        producto = None

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()
            # Puedes agregar lógica adicional aquí, como redireccionar a la página de detalles del producto o mostrar un mensaje de éxito.
            return redirect('lista_productos')  # Redirige a la página de lista de productos o a donde lo necesites
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'agregar_producto.html', {'form': form, 'producto': producto})

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')  # Redirige a la página de lista de proveedores
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'editar_proveedor.html', {'form': form, 'proveedor': producto})

def cambiar_estado(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    producto.estado = not producto.estado  # Cambiar el estado (de True a False o de False a True)
    producto.save()
    return redirect('lista_productos')  # Redirige a la página de lista de productos o a donde lo necesites


from django.shortcuts import render, redirect
from .forms import CategoriaForm

def agregar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')  # Redirige a la página de lista de categorías
    else:
        form = CategoriaForm()
    return render(request, 'agregar_categoria.html', {'form': form})


from django.shortcuts import render, redirect, get_object_or_404
from .forms import CategoriaForm
from .models import Categoria

def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')  # Redirige a la página de lista de categorías
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'editar_categoria.html', {'form': form, 'categoria': categoria})



from django.shortcuts import render, redirect
from .forms import ProveedorForm

def agregar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')  # Redirige a la página de lista de proveedores
    else:
        form = ProveedorForm()
    return render(request, 'agregar_proveedor.html', {'form': form})


from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProveedorForm
from .models import Proveedor

def editar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')  # Redirige a la página de lista de proveedores
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'editar_proveedor.html', {'form': form, 'proveedor': proveedor})


from django.shortcuts import render
from .models import Categoria

def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'lista_categorias.html', {'categorias': categorias})


from django.shortcuts import render
from .models import Proveedor

def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'lista_proveedores.html', {'proveedores': proveedores})

from django.shortcuts import render
from .models import Cliente

def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})

from django.shortcuts import render, redirect
from .forms import ClienteForm

def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')  # Redirige a la página de lista de clientes
    else:
        form = ClienteForm()
    return render(request, 'agregar_cliente.html', {'form': form})



from django.shortcuts import render, redirect, get_object_or_404
from .forms import ClienteForm
from .models import Cliente

def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')  # Redirige a la página de lista de clientes
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'editar_cliente.html', {'form': form, 'cliente': cliente})

from django.shortcuts import render
from .models import Cliente

def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})

# -------------==================== tienda ===========================-------------------

def inicio_Tienda(request):
    return render(request, "tienda/index.html",{})

def acercaDe(request):
    return render(request, "tienda/acercaDe.html",{})

def contactanos(request):
    return render(request, "tienda/contactanos.html",{})
