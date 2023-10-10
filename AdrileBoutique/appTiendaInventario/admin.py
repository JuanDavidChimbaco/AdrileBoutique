from django.contrib import admin
from .models import (Usuario,Categoria,Producto,Proveedor,Cliente,Compra,Venta,
                     DetalleCompra,DetalleVenta)

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Categoria)
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Compra)
admin.site.register(DetalleCompra)
admin.site.register(Venta)
admin.site.register(DetalleVenta)