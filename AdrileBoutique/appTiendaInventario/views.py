from django.shortcuts import render, redirect
from .models import Producto, Categoria
# Create your views here.

def redirect_index(request):
    return redirect("index")

def index(request):
    producto = Producto.objects.all()
    categoria = Categoria.objects.all()
    return render(request,"index.html",{"productos":producto, "categorias":categoria})