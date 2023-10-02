from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.

#================================= Usuario ==============================================
class Usuario(User):
    telefono = models.CharField(max_length=45)
    fechaNacimiento = models.DateField()
    direccion = models.CharField(max_length=45)
    fotoPerfil = models.ImageField(upload_to="perfiles/", blank=True, null=True)

    def __str__(self):
        return self.username


# ================================= Categoria ==============================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    imagen = models.ImageField(upload_to="categorias/", blank=True, null=True)
    categoria_padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre


# ============================== Productos ===========================
class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    estado = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre

# ============================== Productos ===========================
class Talla(models.Model):
    talla = models.CharField(max_length=10)
    cantidad = models.IntegerField()
    producto = models.ForeignKey(Producto, related_name="tallas", on_delete=models.PROTECT)

    def __str__(self):
        return  f"{self.producto.nombre} Talla: {self.talla}"


# ================================= Pedido ==============================================
# ESTADOPEDIDO = (
#     ("pendiente", "Pendiente"),
#     ("confirmado", "Confirmado"),
#     ("devuelto", "Devuelto"),
# )

# class Pedido(models.Model):
#     codigoPedido = models.CharField(max_length=45, unique=True)
#     fechaPedido = models.DateField()
#     usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
#     total = models.DecimalField(max_digits=10, decimal_places=2)
#     estadoPedido = models.CharField(max_length=50, default="pendiente")

#     def __str__(self):
#         return f"Pedido {self.codigoPedido}"


# class DetallePedido(models.Model):
#     pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT)
#     producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
#     talla = models.ForeignKey(Talla, on_delete=models.PROTECT)
#     cantidad = models.IntegerField()
#     subtotal = models.FloatField()

#     def __str__(self):
#         return f"Detalle del pedido #{self.pedido.id} - Producto: {self.producto.nombre}, Talla: {self.talla.talla}, Cantidad: {self.cantidad}"


# # ================================= Envio ==============================================
# class Envio(models.Model):
#     pedido = models.OneToOneField(Pedido, on_delete=models.PROTECT)
#     direccionEntrega = models.CharField(max_length=255)
#     codigoPostal = models.CharField(max_length=45)
#     ciudad = models.CharField(max_length=45)
#     departamento = models.CharField(max_length=45)
#     pais = models.CharField(max_length=45)
#     costoEnvio = models.DecimalField(max_digits=10, decimal_places=2)
#     estadoEnvio = models.CharField(max_length=50, default="pendiente")
#     fechaEstimadaEntrega = models.DateField(null=True, blank=True)

#     def __str__(self):
#         return f"Envío para el Pedido {self.pedido.codigoPedido}"
    

# # ================================= Pago ==============================================
# METODOS = (
#     ("tarjetaCredito", "Tarjeta de Credito"),
#     ("tarjetaDebito", "Tarjeta de Debito"),
#     ("contraEntrega", "Contra entrega"),
#     ("PSE", "Pago Seguro en Linea(PSE)"),
# )
# ESTADOPAGO = (
#     ("pendiente", "Pendiente"),
#     ("pagado", "Pagado"),
#     ("rechazado", "Rechazado"),
#     ("cancelado", "Cancelado"),
# )


# class Pago(models.Model):
#     metodo = models.CharField(max_length=45, choices=METODOS)
#     fechaPago = models.DateTimeField()
#     estadoPago = models.CharField(max_length=45, choices=ESTADOPAGO, default="pendiente")
#     confirmado = models.BooleanField(default=False)  # Nuevo campo para la confirmación
#     pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT)

#     def __str__(self):
#         return f"Pago {self.id}"




# # ================================= Devolucion ==============================================
# class Devolucione(models.Model):
#     pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT)
#     motivo = models.CharField(max_length=255)
#     detalles = models.TextField(blank=True, null=True)
#     fechaDevolucion = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Devolución del Pedido {self.pedido.id}"


# # ================================= Carrito ==============================================
# class Cart(models.Model):
#     products = models.ManyToManyField(Producto, through="CartItem")
#     def __str__(self):
#         return f"Cart {self.id}"

# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.PROTECT)
#     product = models.ForeignKey(Producto, on_delete=models.PROTECT)
#     quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
#     def __str__(self):
#         return f"CartItem {self.id}"