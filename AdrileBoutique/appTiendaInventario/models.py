from django.db import models
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Create your models here.
class GroupCreator(models.Model):
    class Meta:
        verbose_name_plural = 'Group Creator'

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    # Define los nombres de los grupos que deseas crear
    group_names = ['administrador', 'empleado']

    # Itera sobre los nombres de los grupos y créalos si no existen
    for group_name in group_names:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f'Se ha creado el grupo: {group_name}')
            
#================================= Usuarios ==============================================
class Usuario(User):
    direccion = models.CharField(max_length=45)
    telefono = models.CharField(max_length=45)
    fotoPerfil = models.ImageField(upload_to="perfiles/", blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

# ================================= Categorias ==============================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    imagen = models.ImageField(upload_to="categorias/", blank=True, null=True)
    categoria_padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre

# ================================= Proveedores ========================
class Proveedor(models.Model):
    nombre_empresa = models.CharField(max_length=100)
    nombre_contacto = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    correo_electronico = models.EmailField()
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre_empresa
    
# ============================== Productos ===========================
DISPONIBLE = True
AGOTADO = False
ESTADO_CHOICES = [
        (DISPONIBLE, 'Disponible'),
        (AGOTADO, 'Agotado'),
    ]
class Producto(models.Model):
    codigo = models.IntegerField(unique=True,null=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    estado = models.BooleanField(choices=ESTADO_CHOICES, default=DISPONIBLE)
    talla = models.CharField(max_length=10)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    cantidad_stock = models.IntegerField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

# ============================== Clientes ===========================
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    correo_electronico = models.EmailField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# ===================[Compras]========================
class Compra(models.Model):
    fecha_compra = models.DateTimeField(auto_now_add=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    def __str__(self):
        return f"Compra #{self.id} - {self.fecha_compra}"

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle de compra #{self.id}"

    
# ====================[Ventas]==============================
class Venta(models.Model):
    fecha_venta = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)                              

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_venta}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle de venta #{self.id}"
    