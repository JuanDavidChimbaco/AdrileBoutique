"""
URL configuration for AdrileBoutique project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from appTiendaInventario import views

# router para las rutas de la Api
router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'categorias', views.CategoriaViewSet)
router.register(r'proveedores', views.ProveedorViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'clientes', views.ClienteViewSet)
router.register(r'compras', views.CompraViewSet)
router.register(r'detalles_compra', views.DetalleCompraViewSet)
router.register(r'ventas', views.VentaViewSet)
router.register(r'detalles_venta', views.DetalleVentaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('index', views.index, name='index'),
    # rutas de la Api
    path("api/", include(router.urls)),
    
    # URL para iniciar sesión y para cerrar sesión
    path('login/', views.login_view, name='login'),
    path("logout/", views.custom_logout, name="logout"),
    
    # gestion de Perfil
    path("perfil/<int:usuario_id>/", views.perfil_usuario, name="perfil"),

    
    # funciones extras
    path('autocomplete_product_name/', views.autocomplete_product_name, name='autocomplete_product_name'),
    
    # URL de gestion inventario
    path('dashboard/', views.dashboard, name='dashboard'),
    path("frmCategorias/", views.categorias, name="categorias"),
    path("frmProductos/", views.productos, name="productos"),
    path("frmEntradas/", views.entradas, name="entradas"),
    path("frmSalidas/", views.salidas, name="salidas"),
    
    
     path('crear_compra_api/', views.CrearCompra.as_view(), name='crear_compra_api'),
     path('productos_por_proveedor/<int:proveedor_id>/', views.productos_por_proveedor, name='productos_por_proveedor'),
     
    
    # formularios
    path('proveedores/', views.proveedores, name='proveedores'),
    path('clientes/', views.clientes, name='clientes'),

    # URL para restablecer contraseña
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
