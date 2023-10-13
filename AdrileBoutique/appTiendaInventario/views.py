from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


from rest_framework import viewsets, status
from rest_framework.views import APIView
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

# Create your views here.


# ===[login y logout sin Api]===
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


# ===[vistas templates]===
@login_required(login_url="index")
def inicio(request):
    return redirect("dashboard")


def index(request):
    return render(request, "index.html", {})


@login_required(login_url="index")
def dashboard(request):
    pertenece_a_administrador = request.user.groups.filter(
        name="administrador"
    ).exists()
    return render(
        request,
        "inventario/dashboard.html",
        {"user": request.user, "es_administrador": pertenece_a_administrador},
    )


@login_required(login_url="index")
def perfil_usuario(request, usuario_id):
    usuario = Usuario.objects.get(pk=usuario_id)
    pertenece_a_administrador = request.user.groups.filter(
        name="administrador"
    ).exists()
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
    return render(request, "inventario/frmEntrada.html", {"proveedores": proveedores})


@login_required(login_url="index")
def salidas(request):
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()
    return render(request,"inventario/frmSalidas.html",{"clientes": clientes, "productos": productos})


# ===[Funciones Extras]===
def autocomplete_product_name(request):
    term = request.GET.get("term", "")
    products = Producto.objects.filter(nombre__icontains=term).values_list(
        "nombre", flat=True
    )
    return JsonResponse(list(products), safe=False)


# ===[Api]===
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


class DetalleCompraViewSet(viewsets.ModelViewSet):
    queryset = DetalleCompra.objects.all()
    serializer_class = DetalleCompraSerializer


class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer


class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer


# ===[otros metodos]===
class CrearCompra(APIView):
    def post(self, request, format=None):
        compra_serializer = CompraSerializer(data=request.data)
        if compra_serializer.is_valid():
            compra = compra_serializer.save()

            detalles_data = request.data.get("detalles")
            for detalle_data in detalles_data:
                detalle_data["compra"] = compra.id
                detalle_serializer = DetalleCompraSerializer(data=detalle_data)
                if detalle_serializer.is_valid():
                    detalle_serializer.save()

                    # Actualiza el stock del producto
                    producto = Producto.objects.get(id=detalle_data["producto"])
                    cantidad_comprada = detalle_data["cantidad"]
                    producto.cantidad_stock += int(cantidad_comprada)
                    producto.save()

                else:
                    # Maneja el error en caso de detalles no válidos
                    return Response(
                        detalle_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(compra_serializer.data, status=status.HTTP_201_CREATED)
        return Response(compra_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class CrearVenta(APIView):
    def post(self, request, format=None):
        venta_serializer = VentaSerializer(data=request.data)
        if venta_serializer.is_valid():
            venta = venta_serializer.save()
            
            detalles_data = request.data.get('detalles')
            for detalle_data in detalles_data:
                detalle_data['venta'] = venta.id
                detalle_serializer = DetalleVentaSerializer(data=detalle_data)
                if detalle_serializer.is_valid():
                    detalle_serializer.save()
                    
                    # Actualiza el stock del producto
                    producto = Producto.objects.get(id=detalle_data['producto'])
                    cantidad_vendida = detalle_data['cantidad']
                    if cantidad_vendida > producto.cantidad_stock:
                        return Response({'error': 'No hay suficiente stock para este producto'}, status=status.HTTP_400_BAD_REQUEST)
                    producto.cantidad_stock -= cantidad_vendida
                    producto.save()
                else:
                    # Maneja el error en caso de detalles no válidos
                    return Response(detalle_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(venta_serializer.data, status=status.HTTP_201_CREATED)
        return Response(venta_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.shortcuts import render, redirect
from .forms import CompraForm, DetalleCompraForm
from .models import Compra, DetalleCompra
from django.views.generic import View

class EntradaInventarioView(View):
    def get(self, request):
        compra_form = CompraForm()
        detalle_form = DetalleCompraForm()
        return render(request, 'entrada_inventario.html', {'compra_form': compra_form, 'detalle_form': detalle_form})

    def post(self, request):
        compra_form = CompraForm(request.POST)
        detalle_form = DetalleCompraForm(request.POST)
        
        if compra_form.is_valid() and detalle_form.is_valid():
            compra = compra_form.save()  # Guardar la información de la compra
            
            # Obtener los datos del formulario de detalle
            producto = detalle_form.cleaned_data['producto']
            cantidad = detalle_form.cleaned_data['cantidad']
            precio_unitario = detalle_form.cleaned_data['precio_unitario']
            
            # Crear un nuevo registro de detalle de compra
            detalle_compra = DetalleCompra(compra=compra, producto=producto, cantidad=cantidad, precio_unitario=precio_unitario)
            detalle_compra.save()
            
            # Puedes redirigir a la misma página o a otra, según tu preferencia
            return redirect('entrada_inventario')
        
        # Si los formularios no son válidos, puedes manejar los errores aquí
        return render(request, 'entrada_inventario.html', {'compra_form': compra_form, 'detalle_form': detalle_form})


    
    
from django.shortcuts import render
from .models import Compra

def lista_compras(request):
    compras = Compra.objects.all()  # Recupera todas las compras en la base de datos
    return render(request, 'lista_compras.html', {'compras': compras})

from django.shortcuts import render, redirect
from .models import Cliente, Producto
from .forms import VentaForm

def registrar_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            cliente = form.cleaned_data['cliente']
            productos = form.cleaned_data['productos']
            cantidades = form.cleaned_data['cantidades'].split(',')  # Dividir las cantidades ingresadas

            for producto, cantidad in zip(productos, cantidades):
                cantidad = int(cantidad)
                if cantidad > 0:
                    # Asegúrate de que haya suficiente stock antes de procesar la venta
                    if producto.cantidad_stock >= cantidad:
                        # Registrar la venta (puedes crear un modelo Venta para esto)
                        venta = Venta(cliente=cliente)
                        venta.save()
                        
                        # Actualizar el stock
                        producto.cantidad_stock -= cantidad
                        producto.save()
            return redirect('lista_ventas')  # Redirige a la página de lista de ventas o a donde lo necesites
    else:
        form = VentaForm()
    
    return render(request, 'registrar_venta.html', {'form': form})


from django.shortcuts import render
from .models import Venta

def lista_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'lista_ventas.html', {'ventas': ventas})

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

