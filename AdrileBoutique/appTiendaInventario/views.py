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
