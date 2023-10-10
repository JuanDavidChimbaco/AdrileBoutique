from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required(login_url='index')
def inicio(request):
    return redirect("dashboard")

def index(request):
    return render(request,"index.html",)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)  # La sesión expirará cuando se cierre el navegador
            return redirect('dashboard')
        else:
            # El inicio de sesión falló, muestra un mensaje de error
            error_message = "Nombre de usuario o contraseña incorrectos."
            return render(request, "index.html", {'error_message':error_message} )
    return render(request, 'index.html', locals())

@login_required(login_url='index')
def custom_logout(request):
    logout(request)
    return redirect("index")

@login_required(login_url='index')
def dashboard(request):
    return render (request, 'inventario/dashboard.html')

@login_required(login_url='index')
def perfil_usuario(request):
    return render(request, "inventario/perfil.html", {})