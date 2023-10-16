window.addEventListener('load', function () {
    var loaderWrapper = document.querySelector('.loader-wrapper');
    loaderWrapper.style.display = 'none';
});

window.onscroll = function () {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        var scrollToTop = document.querySelector('.scroll-to-top');
        if (scrollToTop) {
            scrollToTop.style.display = 'block';
        }
    } else {
        var scrollToTop = document.querySelector('.scroll-to-top');
        if (scrollToTop) {
            scrollToTop.style.display = 'none';
        }
    }
};

document.addEventListener('DOMContentLoaded', function () {
    var scrollToTop = document.querySelector('.scroll-to-top');
    if (scrollToTop) {
        scrollToTop.addEventListener('click', function () {
            document.body.scrollTop = 0; // Para navegadores antiguos
            document.documentElement.scrollTop = 0; // Para navegadores modernos
        });
    }
});

async function get_categories() {
    let data = '';
    let data2 = '';
    try {
        const response = await axios.get('/api/v1.0/categoriaCliente/');
        response.data.forEach((category) => {
            data += `
                   <a class="categoriaitem" data-bs-toggle="collapse" href="#collapseExample" role="button" aria-expanded="false" aria-controls="collapseExample" onclick="ProductsByCategory(${category.id})">
                        <img src="${category.imagen}" alt="categoria" class="rounded-circle border border-opacity-25 border-secondary imagenCategoria" width="100" height="100">
                        <span class="fw-bold">${category.nombre}</span>
                   </a>
              `;
            data2 += `
              <li><a class="dropdown-item" data-bs-toggle="collapse" href="#collapseExample" role="button" aria-expanded="false" aria-controls="collapseExample" onclick="ProductsByCategory(${category.id})"> ${category.nombre}</a></li>
        `;
        });
        listaCategorias.innerHTML = data2;
        contenedorCategorias.innerHTML = data;
    } catch (error) {
        console.error(error);
    }
}

function viewLogin() {
    let login = document.getElementById('login');
    login.style.display = block;
}

async function login() {
    const formData = {
        username: id_username.value,
        password: id_password.value,
        rememberme: remember_me.value,
    };
    axios.defaults.xsrfCookieName = 'csrftoken'; // Nombre de la cookie CSRF
    axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // Nombre del encabezado CSRF;
    try {
        const response = await axios.post('/api/v1.0/sesion_cliente/', formData);
        console.log(response);
        Swal.fire({
            position: 'center',
            icon: 'success',
            iconColor: '#2ECC71',
            title: '¡Genial! ' + response.data.message,
            showConfirmButton: true,
            confirmButtonColor: '#17202A',
            allowOutsideClick: false,
        }).then(() => {
            if (response.data.user.groups[0] === 2) {
                var miModal = document.getElementById('exampleModal');
                this.username = '';
                this.password = '';
                this.rememberme = false;
                $(miModal).modal('hide');
                location.reload();
            }
            if (response.data.user.groups[0] === 1) {
                window.location.href = '/dashboard/';
            }
        });
    } catch (error) {
        console.error(error.response.data);
        Swal.fire({
            position: 'center',
            icon: 'error',
            title: 'Oops... ' + error.response.data.message,
            showConfirmButton: false,
            allowOutsideClick: false,
            timer: 2000,
        }).then(() => {
            id_username.value = '';
            id_password.value = '';
            remember_me.value = false;
        });
    }
}

async function ProductsByCategory(idCategoria) {
    let productByCategory = document.getElementById('productosPorCategoria');
    let data = '';
    try {
        const response = await axios.get(`/productos/categoria/${idCategoria}/`);
        response.data.forEach((product) => {
            // Formatear el precio con puntos de mil
            const precioConPuntosDeMil = parseFloat(product.precio).toLocaleString('es-ES', { style: 'currency', currency: 'COP' });

            data += `
            <a class="linkCard" href="/detalle_producto?id=${product.id}" onclick="productoSeleccionado(${product.id})">
                <div class="card producto-card" height="300">
                <h3>${product.nombre}</h3>
                <div class="card-body">
                    <img src="${product.imagen}" alt="producto" class="card-img-top " width="100" height="150">
                        <p class="card-text">${product.descripcion}</p>
                        <p class="card-text">Precio: ${precioConPuntosDeMil}</p>
                    </div>
                </div>
            </a>
        `;
        });
        productByCategory.innerHTML = data;

    } catch (error) { }
}

//-------------------Funcion de Autocompletado ------------------
function autoComplete() {
    if(e.keyCode == 13) {
        e.preventDefault();
      }
    fetch(`/api/v1.0/productosPaginacion2/?limit=100offset=0`)
        .then(response => response.json())
        .then(data => {
            let textoBuscar = document.getElementById("txtBuscar").value
            if (textoBuscar.length >= 2) {
                let lista = `<div class='list-group'>`
                let filtroProducto = data.filter(filtrarP)
                filtroProducto.forEach(element => {
                    iconoProducto(element.id)
                    lista += `<a class='list-group-item list-group-item-action' href="/detalle_producto?id=${element.id}" onclick="${productoSeleccionado(element.id)}">${element.nombre} <img id="icono${element.imagen}" style="width:20%"></a>`
                });
                lista += `</div>`
                document.getElementById("listaProductos").innerHTML = lista
                document.getElementById("listaProductos").style = `position:absolute;top:38px;width:100%;z-index:2000; height:600px;overflow:auto;`
            }
            if (textoBuscar == 0) {
                document.getElementById("listaProductos").innerHTML = ""
            }
        })

}

//-------------------Funcion Filtrar producto------------------
function filtrarP(element) {
    let textoBuscar = document.getElementById("txtBuscar").value
    let nombre = element.nombre
    return nombre.includes(textoBuscar.toLowerCase())
}

//------------------Funcion Icono producto---------------------
function iconoProducto(id) {
    fetch('/api/v1.0/productosCliente/'+id)        
        .then(response => response.json())
        .then(data => {
            document.getElementById(`icono${data.imagen}`).src = data.imagen
        })
}

//cargar las categorias apenas cargue el DOOM
get_categories();

function productoSeleccionado(id) {
    localStorage.setItem('productoSeleccionado', id);
}