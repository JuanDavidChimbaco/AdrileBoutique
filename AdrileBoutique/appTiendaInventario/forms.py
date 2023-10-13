from django import forms
from .models import Compra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = '__all__'

from django import forms 
from .models import  DetalleCompra

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = '__all__'
        
# =======================================================================
from django import forms
from .models import Compra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor']

    def __init__(self, *args, **kwargs):
        super(CompraForm, self).__init__(*args, **kwargs)
        self.fields['proveedor'].widget.attrs['class'] = 'selectpicker'  # Añade clases CSS si es necesario
        self.fields['proveedor'].queryset = Proveedor.objects.all()  # Ajusta el queryset según tus necesidades
        
# forms.py
from django import forms
from .models import DetalleCompra

DetalleCompraFormSet = forms.inlineformset_factory(Compra, DetalleCompra, fields=['producto', 'cantidad', 'precio_unitario'])
        
# =============================================================================================================

from django import forms
from .models import Venta

class VentaForm(forms.Form):
    class Meta:
        model = Venta
        fields = '__all__'

from django import forms
from .models import DetalleVenta

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = '__all__'
    
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
