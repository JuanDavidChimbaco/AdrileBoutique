from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.http import Http404
from django.db import transaction
from django.conf import settings

import os
import logging

logger = logging.getLogger(__name__)

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

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

# Importa los módulos necesarios correo
from django.core.mail import send_mail
from django.shortcuts import render
from django.conf import settings
import threading

#================== de prueba ==================================
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Producto,Categoria,Proveedor,DetalleVenta,Venta,Cliente
from .forms import ProductoForm,CategoriaForm,ProveedorForm,ClienteForm

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
                # Si remember_me no está marcado, establece la sesión para que expire después de 1 hora
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            else:
                # Si remember_me está marcado, la sesión no expirará cuando se cierre el navegador
                request.session.set_expiry(0)
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
def lista_compras(request):
    compras = Compra.objects.annotate(total_cantidad=Sum('detallecompra__cantidad'))
    for compra in compras:
        compra.fecha_compra = compra.fecha_compra.strftime('%Y-%m-%d')
    return render(request, 'lista_compras.html', {'compras': compras})


@login_required(login_url="index")
def salidas(request):
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()
    return render(request,"inventario/frmSalidas.html",{"clientes": clientes, "productos": productos})


@login_required(login_url="index")
def lista_ventas(request):
    ventas = Venta.objects.annotate(total_cantidad=Sum('detalleventa__cantidad'))
    for venta in ventas:
        venta.fecha_venta = venta.fecha_venta.strftime('%Y-%m-%d')
    return render(request, 'lista_ventas.html', {'ventas': ventas})


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


class DetalleCompraPorCompraViewSet(viewsets.ModelViewSet):
    serializer_class = DetalleCompraSerializer

    def get_queryset(self):
        queryset = DetalleCompra.objects.all()
        compra_id = self.request.query_params.get('compra')# Obtener el valor del parámetro 'compra' de la solicitud (si existe)
        if compra_id:
            queryset = queryset.filter(compra=compra_id)# Filtrar por compra si se proporciona el parámetro 'compra'
        return queryset


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


class DetalleVentaPorVentaViewSet(viewsets.ModelViewSet):
    serializer_class = DetalleVentaSerializer

    def get_queryset(self):
        queryset = DetalleVenta.objects.all()
        venta_id = self.request.query_params.get('venta')# Obtener el valor del parámetro 'venta' de la solicitud (si existe)
        if venta_id:
            queryset = queryset.filter(venta=venta_id)# Filtrar por venta si se proporciona el parámetro 'venta'
        return queryset


# ===[login y logout con Api]===========================================================================================
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Verificar las credenciales del usuario
    user = authenticate(username=username, password=password)

    if user is not None:
        # El usuario es válido, generar un token de acceso
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Devolver el token de acceso en la respuesta
        return Response({'access_token': access_token})
    else:
        return Response({'message': 'Nombre de usuario o contraseña incorrectos'}, status=status.HTTP_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_api_view(request):
    # Invalidar el token de acceso forzando su expiración
    refresh_token = RefreshToken(request.data['refresh_token'])
    refresh_token.blacklist()

    return Response({'message': 'Cierre de sesión exitoso'})


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


# -------------==================== tienda ===========================-------------------
def inicio_Tienda(request):
    return render(request, "tienda/index.html",{})

def acercaDe(request):
    return render(request, "tienda/acercaDe.html",{})

def contactanos(request):
    return render(request, "tienda/contactanos.html",{})

def inicioTienda(request):
    return render(request, "tienda/inicio.html",{})


def enviarCorreo(asunto, mensaje, destinatarios):
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, destinatarios, fail_silently=False)


# Función para enviar correo electrónico
def enviarCorreo(asunto, mensaje, remitente, destinatario):
    send_mail(asunto, mensaje, remitente, [destinatario], fail_silently=False)


# Vista para la página de contacto
def contact(request):
    if request.method == 'POST':
        if 'name' in request.POST and 'email' in request.POST and 'message' in request.POST:
            message_name = request.POST['name']
            message_email = request.POST['email']
            message = request.POST['message']

            if message_name and message_email and message:  # Verifica si todos los campos están completos
                asunto = 'Mensaje de la tienda de ropa femenina'
                mensajeCorreo = f'El cliente {message_name} con la dirección de correo {message_email} ha enviado el siguiente mensaje: {message}'

                thread = threading.Thread(target=enviarCorreo, args=(asunto, mensajeCorreo, message_email, settings.EMAIL_HOST_USER))
                thread.start()

                mensaje = 'Mensaje enviado, pronto nos pondremos en contacto contigo.'
                return render(request, 'tienda/contactanos.html', {'mensaje': mensaje})
            else:
                mensaje_Complete = 'Asegúrate de completar todos los campos.'
                return render(request, 'tienda/contactanos.html', {'mensaje_Complete': mensaje_Complete})
        else:
            mensaje_E = 'Campos faltantes.'
            return render(request, 'tienda/contactanos.html', {'mensaje_E': mensaje_E})
    else:
        mensaje_Error = 'Intentalo más tarde.'
        return render(request, 'tienda/contactanos.html', {'mensaje_Error': mensaje_Error})
    
    
# ====================[pruebas sin diseño ]================================================================
def lista_stock(request):
    productos = Producto.objects.all()
    return render(request, 'lista_stock.html', {'productos': productos})


def informe_ventas(request):
    ventas = Venta.objects.all()
    total_ventas = ventas.aggregate(total=Sum('detalleventa__cantidad'))

    return render(request, 'informe_ventas.html', {'ventas': ventas, 'total_ventas': total_ventas})


def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'lista_productos.html', {'productos': productos})


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


def agregar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')  # Redirige a la página de lista de categorías
    else:
        form = CategoriaForm()
    return render(request, 'agregar_categoria.html', {'form': form})


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


def agregar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')  # Redirige a la página de lista de proveedores
    else:
        form = ProveedorForm()
    return render(request, 'agregar_proveedor.html', {'form': form})


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


def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'lista_categorias.html', {'categorias': categorias})


def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'lista_proveedores.html', {'proveedores': proveedores})


def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})


def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')  # Redirige a la página de lista de clientes
    else:
        form = ClienteForm()
    return render(request, 'agregar_cliente.html', {'form': form})


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


def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})


