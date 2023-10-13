from django import forms
from .models import Compra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = '__all__'

from django import forms
from .models import DISPONIBLE, Cliente, DetalleCompra, Producto

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = '__all__'
        
from django.forms import modelformset_factory

DetalleCompraFormSet = modelformset_factory(DetalleCompra, form=DetalleCompraForm, extra=1)

from django import forms

class VentaForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all())
    productos = forms.ModelMultipleChoiceField(queryset=Producto.objects.filter(estado=DISPONIBLE))
    cantidades = forms.CharField()  # Puedes usar un campo de texto separado por comas o algún otro formato
    
    
from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'descripcion', 'precio', 'talla', 'categoria', 'cantidad_stock', 'proveedor', 'imagen', 'estado']

from django import forms
from .models import Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'
        
from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'
        
from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
