from rest_framework import serializers
from .models import Usuario, Categoria, Proveedor, Producto, Cliente, Compra, DetalleCompra, Venta, DetalleVenta

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class DetalleCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCompra
        fields = '__all__'

class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = '__all__'

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'

class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = '__all__'
        
from django.contrib.auth.forms import PasswordResetForm
           
class CustomPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Valida si el correo electrónico existe en la base de datos.
        PasswordResetForm({'email': value})  # Utiliza Django's PasswordResetForm para validar el correo electrónico.

        return value

# Serializer para el registro de usuarios (Solo para los empleados)
class RegistroEmpleadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "telefono",
            "direccion",
            "fotoPerfil",
        ]
        extra_kwargs = {"password": {"write_only": True}}


# Serializer para el login de usuarios (solo para el empleado)
class LoginUsuarioSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True
    )  # Marcar la contraseña como solo escritura