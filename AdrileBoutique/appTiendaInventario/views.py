from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse,Http404
from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import EmailMessage


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


import smtplib
from datetime import datetime, timedelta
import os
import logging
import matplotlib.pyplot as plt
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

from rest_framework import viewsets, status, permissions
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

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
    DISPONIBLE,
    AGOTADO
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
    LoginUsuarioSerializer,
    CustomPasswordResetSerializer,
)

# Importa los módulos necesarios correo
from django.core.mail import send_mail
from django.shortcuts import render
from django.conf import settings
import threading

# ================== de prueba ==================================
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Producto, Categoria, Proveedor, DetalleVenta, Venta, Cliente
from .forms import ProductoForm, CategoriaForm, ProveedorForm, ClienteForm

# Create your views here.


# ===[login y logout sin Api]=======================================================================0
@api_view(["POST"])
@permission_classes([AllowAny])
def login_api_view(request):
    serializer = LoginUsuarioSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        # Verificar las credenciales del usuario
        user = authenticate(username=username, password=password)
        if user:
            remember_me = request.data.get("remember_me", False)  # Agrega un campo "remember_me" al formulario o solicitud de inicio de sesión
            if not remember_me:
                # Configurar la sesión del usuario para que expire cuando el navegador se cierre
                request.session.set_expiry(0)

            # Iniciar sesión del usuario
            login(request, user)

            token, _ = Token.objects.get_or_create(user=user)
            return Response({"auth_token": token.key})
    
    return Response(
        {"message": "Nombre de usuario o contraseña incorrectos"},
        status=status.HTTP_401_UNAUTHORIZED,
    )

# funcion para cerrar sesion :v 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api_view(request):
    # Cierra la sesión del usuario
    logout(request)
    return Response({"message": "Sesión cerrada exitosamente"})

# ===[vistas templates]===============================================================================
@login_required
def inicio(request):
    return redirect("dashboard")


def index(request):
    return render(request, "index.html", {})


def restPasswordRequest(
    request,
):  # vista para validar correo y enviar el enlace de restablecimiento
    return render(request, "registration/restablecer_password.html")


def mensajeCorreo(request):  # vista para mostrar mensaje de que se envio el correo
    return render(request, "registration/mensaje_correo.html")


def restPassword(request):  # vista para digitar la nueva contraseña
    token = request.GET.get("token", "")
    return render(
        request, "registration/restablecer_password_form.html", {"token": token}
    )


@login_required(login_url="login")
def dashboard(request):
    pertenece_a_administrador = request.user.groups.filter(
        name="administrador"
    ).exists()
    retorno = {"user": request.user, "es_administrador": pertenece_a_administrador}
    return render(request, "inventario/dashboard.html", retorno)


@login_required(login_url="login")
def perfil_usuario(request, usuario_id):
    print("ID del usuario logueado:", request.user.id)
    print("ID del usuario solicitado:", usuario_id)
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
        print("Usuario encontrado:", usuario)
    except Usuario.DoesNotExist:
        raise Http404("Usuario no encontrado")
    pertenece_a_administrador = request.user.groups.filter(
        name="administrador"
    ).exists()
    return render(
        request,
        "inventario/perfil.html",
        {"usuario": usuario, "es_administrador": pertenece_a_administrador},
    )


@login_required(login_url="login")
def categorias(request):
    return render(request, "inventario/frmCategorias.html", {})


@login_required(login_url="login")
def productos(request): 
    proveedores = Proveedor.objects.all()
    categorias = Categoria.objects.all()
    return render(
        request,
        "inventario/frmProductos.html",
        {"proveedores": proveedores, "categorias": categorias},
    )


@login_required(login_url="login")
def proveedores(request):
    return render(request, "inventario/frmProveedores.html", {})


@login_required(login_url="login")
def clientes(request):
    return render(request, "inventario/frmClientes.html", {})


@login_required(login_url="login")
def entradas(request):
    proveedores = Proveedor.objects.all()
    productos = Producto.objects.all()
    return render(
        request,
        "inventario/frmEntrada.html",
        {"proveedores": proveedores, "productos": productos},
    )


@login_required(login_url="login")
def lista_compras(request):
    compras = Compra.objects.annotate(total_cantidad=Sum("detallecompra__cantidad"))
    for compra in compras:
        compra.fecha_compra = compra.fecha_compra.strftime("%Y-%m-%d")
    return render(request, "lista_compras.html", {"compras": compras})


@login_required(login_url="login")
def salidas(request):
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()
    return render(
        request,
        "inventario/frmSalidas.html",
        {"clientes": clientes, "productos": productos},
    )


@login_required(login_url="login")
def lista_ventas(request):
    ventas = Venta.objects.annotate(total_cantidad=Sum("detalleventa__cantidad"))
    for venta in ventas:
        venta.fecha_venta = venta.fecha_venta.strftime("%Y-%m-%d")
    return render(request, "lista_ventas.html", {"ventas": ventas})


# ===[Api]========================================================================================================
# crud basico de usuarios se usa como api, requiere autenticacion
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

# crud basico de categorias se usa como api, requiere autenticacion
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

# crud basico de categorias se usa como api pero solo se puede hacer get y no requiere autenticacion
class CategoriaViewSetCliente(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    authentication_classes = []  # Deshabilita la autenticación
    permission_classes = [permissions.AllowAny]  # Permite a cualquiera acceder

# # crud basico de proveedores se usa como api, requiere autenticacion
class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

# crud basico de prodcutos se usa como api pero solo se puede hacer get y no requiere autenticacion
class ProductoViewSetCliente(viewsets.ReadOnlyModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    authentication_classes = []  # Deshabilita la autenticación
    permission_classes = [permissions.AllowAny]  # Permite a cualquiera acceder

# crud basico de productos se usa como api, requiere autenticacion
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

# me lista los productos por el id de la categoria que le pase, solo get y no requiere autenticacion
class ProductosPorCategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoSerializer
    authentication_classes = []  # Deshabilita la autenticación
    permission_classes = [permissions.AllowAny]  # Permite a cualquiera acceder

    def get_queryset(self):
        categoria_id = self.kwargs.get("categoria_id")
        return Producto.objects.filter(categoria__id=categoria_id)

# configura la paginacion de api_rest_framework
class ProductoPagination(PageNumberPagination):
    page_size = 4  # Número de productos por página
    page_size_query_param = "page_size"
    max_page_size = 10  # Límite máximo de productos por página

# pagina los productos utilizando la configuracion anterior, solo get y no requiere autenticacion
class ProductoPaginationViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []  # Deshabilita la autenticación
    permission_classes = [permissions.AllowAny]  # Permite a cualquiera acceder
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    pagination_class = ProductoPagination  # Asigna la paginación personalizada

# pagina productos utilizando la forma limit & offset ,solo get, y no requiere autenticacion 
class ProductoPaginationLimitViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []  # Deshabilita la autenticación
    permission_classes = [permissions.AllowAny]  # Permite a cualquiera acceder
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    pagination_class = LimitOffsetPagination

# crud basico para clientes, requiere autenticacion
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

# se crea la compra, se le pasa un proveedor y los detalles de la compra, 
# los detelles pueden traer varios productos, requiere autenticacion
from reportlab.lib.styles import ParagraphStyle

class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    def create(self, request):
        proveedor_id = request.data.get("proveedor")
        detalles = request.data.get("detalles")

        compra = Compra.objects.create(proveedor_id=proveedor_id)
        proveedor = Proveedor.objects.get(pk=proveedor_id)


        productos_adquiridos = []
        total_a_pagar = 0

        for detalle_data in detalles:
            producto_id = detalle_data.get("producto")
            cantidad = detalle_data.get("cantidad")
            precio_unitario = detalle_data.get("precio_unitario")

            DetalleCompra.objects.create(
                compra=compra,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
            )

            producto = Producto.objects.get(id=producto_id)
            producto.cantidad_stock += cantidad
            producto.save()

            precio_total = cantidad * precio_unitario  # Corregido el cálculo del precio total
            total_a_pagar += precio_total

            productos_adquiridos.append(f" {proveedor.nombre_empresa} - {producto.nombre} - {cantidad} - {precio_unitario} - {precio_total}")

        pdf_filename = f"AdrileBoutique_{compra.id}.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
        story = []

        

        def create_header_style():
            header_style = ParagraphStyle(
                "header",
                parent=getSampleStyleSheet()["Heading1"],
                textColor=colors.black,
                backColor=colors.lightgrey,
            )
            return header_style

        def create_footer_style():
            footer_style = ParagraphStyle(
                "footer",
                parent=getSampleStyleSheet()["BodyText"],
                textColor=colors.black,
                backColor=colors.lightgrey,
            )
            return footer_style

        header_style = create_header_style()
        footer_style = create_footer_style()

        # Encabezado
        header_text = "Factura de Entrada de producto"
        story.append(Paragraph(header_text, header_style))
        story.append(Spacer(1, 12))

        # Crear una lista para la tabla
        data = [["Proveedor", "Nombre P.", "Cantidad", "Precio Unit.", "Subtotal", "Producto"]]

        # Llenar la lista con los productos adquiridos
        # Llenar la lista con los productos adquiridos
        for producto_adquirido in productos_adquiridos:
            detalle_info = producto_adquirido.split('-')
            proveedor_nombre = detalle_info[0].strip()
            producto_nombre = detalle_info[1].strip()
            cantidad = detalle_info[2].strip()
            precio_unitario = detalle_info[3].strip()
            precio_total = detalle_info[4].strip()
            imagen_producto = Producto.objects.get(nombre=producto_nombre).imagen
            if imagen_producto:
                imagen = Image(imagen_producto.path, width=50, height=50)
                data.append([proveedor_nombre, producto_nombre, cantidad, precio_unitario, precio_total, imagen])
            else:
                data.append([proveedor_nombre, producto_nombre, cantidad, precio_unitario, precio_total, ""])



        # Crear la tabla
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('SIZE', (0, 0), (-1, 0), 12),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ]))

        # Agregar la tabla al story
        story.append(table)
        story.append(Spacer(1, 24))

        # Mostrar el precio total a pagar
        story.append(Paragraph(f"Total: {total_a_pagar:,} COP", footer_style))

        # Pie de página
        footer_text = "SOMOS ADRILE BOUTIQUE"
        story.append(Paragraph(footer_text, footer_style))

        doc.build(story)

        from_email = "jdchimbaco@misena.edu.co"
        to_email = "jdchimbaco@misena.edu.co"

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = "Adrile Boutique - Nueva compra realizada"

        body = f"Haz realizado una entrada de producto. Encuentra adjunto el detalle de tu compra."
        msg.attach(MIMEText(body, 'plain'))

        attachment = open(pdf_filename, "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {pdf_filename}')
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, "sdmbakmgudxcsyro")
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()

        serializer = CompraSerializer(compra)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# crud basico para las compras, requiere autenticacion
class DetalleCompraViewSet(viewsets.ModelViewSet):
    queryset = DetalleCompra.objects.all()
    serializer_class = DetalleCompraSerializer

# trae los detalles de la compra pasandole un id de compra, requiere autenticacion
class DetalleCompraPorCompraViewSet(viewsets.ModelViewSet):
    serializer_class = DetalleCompraSerializer

    def get_queryset(self):
        queryset = DetalleCompra.objects.all()
        compra_id = self.request.query_params.get(
            "compra"
        )  # Obtener el valor del parámetro 'compra' de la solicitud (si existe)
        if compra_id:
            queryset = queryset.filter(
                compra=compra_id
            )  # Filtrar por compra si se proporciona el parámetro 'compra'
        return queryset


class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

    def create(self, request):
        cliente_id = request.data.get("cliente")
        detalles = request.data.get("detalles")

        venta = Venta.objects.create(cliente_id=cliente_id)
        cliente = Cliente.objects.get(pk=cliente_id)

        productos_adquiridos = []
        total_a_pagar = 0
        
        for detalle_data in detalles:
            producto_id = detalle_data.get("producto")
            cantidad = detalle_data.get("cantidad")
            precio_unitario = detalle_data.get("precio_unitario")

            DetalleVenta.objects.create(
                venta=venta,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
            )

            producto = Producto.objects.get(id=producto_id)
            producto.cantidad_stock -= cantidad
            producto.save()
            
            precio_total = cantidad * precio_unitario
            total_a_pagar += precio_total
            productos_adquiridos.append(f"{producto.nombre} - {cantidad} - {producto.precio} - {precio_total}")

        pdf_filename = f"AdrileBoutique_{venta.id}.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
        story = []

        def create_header_style():
            header_style = ParagraphStyle(
                "header",
                parent=getSampleStyleSheet()["Heading1"],
                textColor=colors.white,
                backColor=colors.black,
            )
            return header_style

        def create_footer_style():
            footer_style = ParagraphStyle(
                "footer",
                parent=getSampleStyleSheet()["BodyText"],
                textColor=colors.black,
                backColor=colors.lightgrey,
            )
            return footer_style

        header_style = create_header_style()
        footer_style = create_footer_style()

        # Encabezado
        header_text = "Factura Adrile Boutique"
        story.append(Paragraph(header_text, header_style))
        story.append(Spacer(1, 12))

        # Crear una lista para la tabla
        data = [["Nombre", "Cantidad", "Precio Unit.", "Subtotal", "Producto"]]

        # Llenar la lista con los productos adquiridos
        for producto_adquirido in productos_adquiridos:
            producto_info = producto_adquirido.split('-')
            producto_nombre = producto_info[0].strip()
            imagen_producto = Producto.objects.get(nombre=producto_nombre).imagen
            
            if imagen_producto:
                imagen = Image(imagen_producto.path, width=50, height=50)
                data.append([info.strip() for info in producto_info] + [imagen])
            else:
                data.append([info.strip() for info in producto_info] + [""])

        # Crear la tabla con estilos
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('SIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Agregar la tabla al story
        story.append(table)
        story.append(Spacer(1, 24))

        # Calcular el precio total por producto y el total a pagar
        for producto_adquirido in productos_adquiridos:
            producto_info = producto_adquirido.split('-')

        # Mostrar el total a pagar
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Total: {total_a_pagar:,} COP", footer_style))

        # Pie de página
        footer_text = "Gracias por su compra en Adrile Boutique"
        story.append(Paragraph(footer_text, footer_style))


        doc.build(story)

        from_email = "jdchimbaco@misena.edu.co"
        to_email = cliente.correo_electronico

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = "Adrile Boutique"

        body = f"Cordial saludo {cliente.nombre}, has realizado una compra en la tienda. Encuentra adjunto el detalle de tu compra."
        msg.attach(MIMEText(body, 'plain'))

        attachment = open(pdf_filename, "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {pdf_filename}')
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, "sdmbakmgudxcsyro")
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()

        serializer = VentaSerializer(venta)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# crud basico para las detalles de la venta, requiere autenticacion
class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer

# trae los detalles de la venta pasandole un id de venta, requiere autenticacion
class DetalleVentaPorVentaViewSet(viewsets.ModelViewSet):
    serializer_class = DetalleVentaSerializer

    def get_queryset(self):
        queryset = DetalleVenta.objects.all()
        venta_id = self.request.query_params.get(
            "venta"
        )  # Obtener el valor del parámetro 'venta' de la solicitud (si existe)
        if venta_id:
            queryset = queryset.filter(
                venta=venta_id
            )  # Filtrar por venta si se proporciona el parámetro 'venta'
        return queryset


# ===[login y logout con Api]===========================================================================================


# login de api usando token de api_rest_framework_JWT y configurado en el setting.
@api_view(["POST"])
@permission_classes([AllowAny])
def login_api_view(request):
    serializer = LoginUsuarioSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        rememberMe = request.data.get("rememberme")
        # Verificar las credenciales del usuario
        user = Usuario.objects.filter(username=username).first()
        if user and user.check_password(password):
            login(request, user)
            if rememberMe:
                request.session.set_expiry(2592000)  # 30 días en segundos
            else:
                request.session.set_expiry(0)  # Duración predeterminada
            token, _ = Token.objects.get_or_create(user=user)
            user_data = UsuarioSerializer(user).data
            response =  Response({"auth_token": token.key,"message": "Inicio de sesión exitoso","user": user_data,},status=status.HTTP_200_OK,)
            response.set_cookie("token", token.key)
            return response
        else:
            return Response({"message": "Credenciales inválidas"},status=status.HTTP_401_UNAUTHORIZED,)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# logout de api usando el token anteriormente generado, pasarlo por metodo post, 
# para cerrar la sesión, no requiere autenticacion ya que para eso es el token.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api_view(request):
    request.auth.delete()
    return Response({"message": "Cierre de sesión exitoso"})


# ===[otros metodos]============================================================================================
# metodo de filtrado para que me traiga los productos por proveedor
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


def modificarDatosUserPerfil(request, id):
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
                user = Usuario.objects.get(pk=id)
                user.username = usuario
                user.first_name = nombres
                user.last_name = apellidos
                user.email = email
                user.telefono = telefono
                user.direccion = direccion
                if foto:
                    if user.fotoPerfil and os.path.isfile(user.fotoPerfil.path):
                        os.remove(user.fotoPerfil.path)
                    user.fotoPerfil = foto
                user.save()
                mensaje = "Datos Modificados Correctamente"
                retorno = {"mensaje": mensaje, "estado": True}

                return render(request, "inventario/perfil.html", retorno)

        except Exception as error:
            transaction.set_rollback(True)
            if "user.username" in str(error):
                mensaje = "Ya existe un usuario con este nombre de usuario"
            elif "user.email" in str(error):
                mensaje = "Ya existe un usuario con ese correo electrónico"
            else:
                mensaje = str(error)
            retorno = {"mensaje": mensaje, "estado": False}
            return render(request, "inventario/perfil.html", retorno)


def contact(request):
    if request.method == "POST":
        if all(key in request.POST for key in ["name", "email", "message"]):
            message_name = request.POST["name"]
            message_email = request.POST["email"]
            message = request.POST["message"]

            if message_name and message_email and message:  
                asunto = "Mensaje de Usuario en Adrile Boutique"
                mensajeCorreo = (
                    f"El Usuario {message_name}\n"
                    f"con la dirección de correo {message_email}\n"
                    f"ha enviado el siguiente mensaje en Adrile Boutique:\n"
                    f"{message}"
                )

                thread = threading.Thread(
                    target=enviarCorreo,
                    args=(
                        asunto,
                        mensajeCorreo,
                        [settings.EMAIL_HOST_USER], 
                    ),
                )
                thread.start()

                response_data = {
                    "result": "success",
                    "message": "¡El mensaje se envió con éxito! Pronto nos pondremos en contacto contigo."
                }
                return JsonResponse(response_data)
            else:
                response_data = {
                    "result": "error",
                    "message": "Por favor, asegúrate de completar todos los campos."
                }
                return JsonResponse(response_data)
        else:
            response_data = {
                "result": "error",
                "message": "Hubo un problema al procesar tu solicitud. Inténtalo de nuevo más tarde."
            }
            return JsonResponse(response_data)
    else:
        mensaje_Error = "Inténtalo más tarde."
        return render(request, "tienda/contactanos.html", {"mensaje_Error": mensaje_Error})

# Vista para la página de contacto
def contact(request):
    if request.method == "POST":
        if (
            "name" in request.POST
            and "email" in request.POST
            and "message" in request.POST
        ):
            message_name = request.POST["name"]
            message_email = request.POST["email"]
            message = request.POST["message"]

            if (
                message_name and message_email and message
            ):  # Verifica si todos los campos están completos
                asunto = "Mensaje de la tienda de ropa femenina"
                mensajeCorreo = f"El cliente {message_name} con la dirección de correo {message_email} ha enviado el siguiente mensaje: {message}"

                # Configuración de la función enviarCorreo
                thread = threading.Thread(
                    target=enviarCorreo,
                    args=(
                        asunto,
                        mensajeCorreo,
                        [settings.EMAIL_HOST_USER],  # Agrega aquí la dirección de correo de la tienda
                    ),
                )
                thread.start()

                mensaje = "Mensaje enviado, pronto nos pondremos en contacto contigo."
                return render(request, "tienda/contactanos.html", {"mensaje": mensaje})
            else:
                mensaje_Complete = "Asegúrate de completar todos los campos."
                return render(
                    request,
                    "tienda/contactanos.html",
                    {"mensaje_Complete": mensaje_Complete},
                )
        else:
            mensaje_E = "Campos faltantes."
            return render(request, "tienda/contactanos.html", {"mensaje_E": mensaje_E})
    else:
        mensaje_Error = "Intentalo más tarde."
        return render(
            request, "tienda/contactanos.html", {"mensaje_Error": mensaje_Error}
        )


def enviarCorreo(asunto, mensaje, destinatario):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = ', '.join(destinatario)
    msg['Subject'] = asunto

    body = mensaje
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)  
    text = msg.as_string()
    server.sendmail(settings.EMAIL_HOST_USER, destinatario, text)
    server.quit()


def enviarCorreo(asunto=None, mensaje=None, destinatario=None, archivo=None):
    remitente = settings.EMAIL_HOST_USER
    contenido = f"Destinatario: {destinatario}\nMensaje: {mensaje}\nAsunto: {asunto}\nRemitente: {remitente}"
    try:
        correo = EmailMessage(
            asunto,
            contenido,  # Utilizamos el contenido como el cuerpo del correo
            remitente,
            destinatario,
        )
        if archivo is not None:
            correo.attach_file(archivo)
        correo.send(fail_silently=True)
    except Exception as error:
        print(error)

# Se encarga de enviar el correo electrónico con el enlace de restablecimiento
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.MultipleObjectsReturned:
            # Handle the case when multiple objects are returned
            # Log the issue or raise an appropriate error
            # For example:
            logger.error(f"Multiple users found with email {email}")
            mensaje = "Se ha producido un error. Por favor, póngase en contacto con el soporte."
            return render(
                request, "registration/restablecer_password.html", {"mensaje": mensaje}
            )
        except User.DoesNotExist:
            mensaje = "Correo no encontrado"
            return render(
                request, "registration/restablecer_password.html", {"mensaje": mensaje}
            )
        # Generar el token de restablecimiento
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # se encarga de establecer el usuario y la expiración del token
        payload = jwt_payload_handler(user)
        payload["exp"] = datetime.utcnow() + timedelta(
            hours=1
        )  # Establecer la expiración a 1 hora
        token = jwt_encode_handler(payload)
        # Construir el enlace para la vista de restablecimiento de contraseña
        reset_link = request.build_absolute_uri(
            reverse("nuevaContra") + f"?token={token}"
        )
        # Enviar el correo electrónico con el enlace de restablecimiento
        subject = "Restablecimiento de contraseña"
        message = f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n\n{reset_link}"
        send_mail(subject, message, "info@adrileboutique.com", [email])
        mensaje = "Se ha enviado un enlace de restablecimiento a su correo electrónico."
        return render(request, "registration/mensaje.html", {"mensaje": mensaje})


@permission_classes([AllowAny])
class CustomPasswordResetView(CreateAPIView):
    serializer_class = CustomPasswordResetSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            # Genera un token de recuperación de contraseña
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode

            from django.utils.http import urlsafe_base64_encode

            return Response({'detail': 'Se ha enviado un correo electrónico con instrucciones para restablecer la contraseña.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No se encontró ninguna cuenta asociada a este correo electrónico.'}, status=status.HTTP_400_BAD_REQUEST)

# obtiene el token y la nueva contraseña y actualiza la contraseña del usuario
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        try:
            payload = api_settings.JWT_DECODE_HANDLER(token)
            user = Usuario.objects.get(id=payload["user_id"])
        except Usuario.DoesNotExist:
            return Response(
                {"detail": "El token no es válido."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar la contraseña del usuario
        user.set_password(new_password)
        user.save()
        return render(request, "registration/reset_password_success.html")

# me grafica las ventas y compras por fecha 
def informes_combinados(request):
    # Informe de Ventas
    ventas = Venta.objects.all()
    fechas_ventas = [venta.fecha_venta.strftime('%Y-%m-%d') for venta in ventas]
    montos_ventas = []

    for venta in ventas:
        detalles = DetalleVenta.objects.filter(venta=venta)
        total = sum(detalle.cantidad * detalle.precio_unitario for detalle in detalles)
        montos_ventas.append(total)

    # Informe de Compras
    compras = Compra.objects.all()
    fechas_compras = [compra.fecha_compra.strftime('%Y-%m-%d') for compra in compras]
    montos_compras = []

    for compra in compras:
        detalles = DetalleCompra.objects.filter(compra=compra)
        total = sum(detalle.cantidad * detalle.precio_unitario for detalle in detalles)
        montos_compras.append(total)
        
    # Crear gráfico de barras para Ventas
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    axs[0].bar(fechas_ventas, montos_ventas, color='b')
    axs[0].set_title('Informe de Ventas')
    axs[0].set_xlabel('Fechas')
    axs[0].set_ylabel('Monto en $')
    axs[0].set_ylim(0, max(montos_ventas))  # Ajustar el límite inferior a 0

    # Crear gráfico de barras para Compras
    axs[1].bar(fechas_compras, montos_compras, color='r')
    axs[1].set_title('Informe de Compras')
    axs[1].set_xlabel('Fechas')
    axs[1].set_ylabel('Valor $')
    axs[1].set_ylim(0, max(montos_compras))  # Ajustar el límite inferior a 0

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png).decode()


    return render(request, 'inventario/informe_inventario.html', 
                  {'graphic': graphic, 'fechas_ventas': fechas_ventas, 'fechas_compras': fechas_compras,
                   'montos_ventas': montos_ventas, 'montos_compras': montos_compras,})

# -------------==================== tienda ===========================-------------------
def inicio_Tienda(request):
    return render(request, "tienda/index.html", {})
 

def acercaDe(request):
    return render(request, "tienda/acercaDe.html", {})


def contactanos(request):
    return render(request, "tienda/contactanos.html", {})


def inicioTienda(request):
    return render(request, "tienda/inicio.html", {})


def detalleProduto(request):
    return render(request, "tienda/detalle.html")

# def enviarCorreo(asunto=None, mensaje=None, destinatario=None, archivo=None):
#     remitente = settings.EMAIL_HOST_USER
#     template = get_template('enviarCorreo.html')
#     contenido = template.render({
#         'destinatario': destinatario,
#         'mensaje': mensaje,
#         'asunto': asunto,
#         'remitente': remitente,
#     })
#     try:
#         correo = EmailMessage(
#             asunto,
#             contenido,  # Utilizamos el contenido HTML como el cuerpo del correo
#             remitente,
#             destinatario,
#         )
#         correo.content_subtype = "html"
#         if archivo != None:
#             correo.attach_file(archivo)
#         correo.send(fail_silently=True)
#     except Exception as error:
#         print(error)

# def modificarDatosUserPerfil(request,id):
#     """
#     Modifica los datos de un usuario en su perfil y guarda los cambios en la base de datos.

#     Args:
#         request (HttpRequest): La solicitud HTTP recibida.
#         id (int): El ID del usuario cuyos datos se desean modificar.

#     Returns:
#         HttpResponse: Una respuesta HTTP que redirige al perfil del usuario con un mensaje de éxito o error.
#     """
#     if request.method == "POST":
#         try:
#             cedula = request.POST["txtCedula"]
#             nombres = request.POST["txtNombres"]
#             apellidos = request.POST["txtApellido"]
#             correo = request.POST["txtCorreo"]
#             telefono = request.POST["txtTelefono"]
#             foto = request.FILES.get("fileFoto", False)
#             username = request.POST["txtUserName"]
#             with transaction.atomic():
#                 user = User.objects.get(pk=id)
#                 user.username=username
#                 user.first_name=nombres
#                 user.last_name=apellidos
#                 user.email=correo
#                 user.userCedula=cedula
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
#             if 'userCedula' in str(error):
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





# ====================[pruebas sin diseño ]================================================================
def lista_stock(request):
    productos = Producto.objects.all()
    return render(request, "lista_stock.html", {"productos": productos})


def informe_ventas(request):
    ventas = Venta.objects.all()
    total_ventas = ventas.aggregate(total=Sum("detalleventa__cantidad"))

    return render(
        request, "informe_ventas.html", {"ventas": ventas, "total_ventas": total_ventas}
    )


def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, "lista_productos.html", {"productos": productos})


def agregar_producto(request, producto_id=None):
    if producto_id:
        producto = get_object_or_404(Producto, pk=producto_id)
    else:
        producto = None

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()
            # Puedes agregar lógica adicional aquí, como redireccionar a la página de detalles del producto o mostrar un mensaje de éxito.
            return redirect(
                "lista_productos"
            )  # Redirige a la página de lista de productos o a donde lo necesites
    else:
        form = ProductoForm(instance=producto)
    return render(
        request, "agregar_producto.html", {"form": form, "producto": producto}
    )


def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect(
                "lista_productos"
            )  # Redirige a la página de lista de proveedores
    else:
        form = ProductoForm(instance=producto)
    return render(
        request, "editar_proveedor.html", {"form": form, "proveedor": producto}
    )


def cambiar_estado(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    producto.estado = (
        not producto.estado
    )  # Cambiar el estado (de True a False o de False a True)
    producto.save()
    return redirect(
        "lista_productos"
    )  # Redirige a la página de lista de productos o a donde lo necesites


def agregar_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                "lista_categorias"
            )  # Redirige a la página de lista de categorías
    else:
        form = CategoriaForm()
    return render(request, "agregar_categoria.html", {"form": form})


def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect(
                "lista_categorias"
            )  # Redirige a la página de lista de categorías
    else:
        form = CategoriaForm(instance=categoria)
    return render(
        request, "editar_categoria.html", {"form": form, "categoria": categoria}
    )


def agregar_proveedor(request):
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                "lista_proveedores"
            )  # Redirige a la página de lista de proveedores
    else:
        form = ProveedorForm()
    return render(request, "agregar_proveedor.html", {"form": form})


def editar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    if request.method == "POST":
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect(
                "lista_proveedores"
            )  # Redirige a la página de lista de proveedores
    else:
        form = ProveedorForm(instance=proveedor)
    return render(
        request, "editar_proveedor.html", {"form": form, "proveedor": proveedor}
    )


def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, "lista_categorias.html", {"categorias": categorias})


def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, "lista_proveedores.html", {"proveedores": proveedores})


def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, "lista_clientes.html", {"clientes": clientes})


def agregar_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                "lista_clientes"
            )  # Redirige a la página de lista de clientes
    else:
        form = ClienteForm()
    return render(request, "agregar_cliente.html", {"form": form})


def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect(
                "lista_clientes"
            )  # Redirige a la página de lista de clientes
    else:
        form = ClienteForm(instance=cliente)
    return render(request, "editar_cliente.html", {"form": form, "cliente": cliente})


def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, "lista_clientes.html", {"clientes": clientes})
