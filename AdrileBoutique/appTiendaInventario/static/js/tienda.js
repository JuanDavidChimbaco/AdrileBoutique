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
    //-------------cargar las categorias apenas cargue el DOOM---------
    get_categories();
});

//----------------- obtener categorias -------------------------
async function get_categories() {
    let data = '';
    try {
        const response = await axios.get('/api/categoriasCliente/');
        console.log(response)
        response.data.forEach((category) => {
            data += `
                   <a class="categoriaitem" data-bs-toggle="collapse" href="#collapseExample" role="button" aria-expanded="false" aria-controls="collapseExample" onclick="ProductsByCategory(${category.id})">
                        <img src="${category.imagen}" alt="categoria" class="rounded-circle border border-opacity-25 border-secondary imagenCategoria" width="100" height="100">
                        <span class="fw-bold">${category.nombre}</span>
                   </a>
              `;
        });
        contenedorCategorias.innerHTML = data;
    } catch (error) {
        console.error(error);
    }
}

//---------------- productos por categorias ---------------------
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
    fetch(`/api/productosCliente/`)
        .then(response => response.json())
        .then(data => {
            let textoBuscar = document.getElementById("txtBuscar").value
            if (textoBuscar.length >= 2) {
                let lista = `<div class='list-group'>`;
                let filtroProducto = data.filter(filtrar)
                    console.log(filtroProducto);
                    filtroProducto.forEach(element => {
                        iconoProducto(element.id);
                        lista += `<a class='list-group-item list-group-item-action' href="/detalle_producto?id=${element.id}" onclick="${productoSeleccionado(element.id)}">${element.nombre} <img id="icono${element.imagen}" style="width:20%"></a>`;
                    });
            
                lista += `</div>`;
                document.getElementById("listaProductos").innerHTML = lista;
                document.getElementById("listaProductos").style = `position:absolute;top:38px;width:100%;z-index:2000; height:600px;overflow:auto;`;
            }
            
            if (textoBuscar == 0) {
                document.getElementById("listaProductos").innerHTML = ""
            }
        })
}

//-------------------Funcion Filtrar producto------------------
function filtrar(element) {
    let textoBuscar = document.getElementById("txtBuscar").value
    let nombre = element.nombre
    let filtrado =  nombre.includes(textoBuscar.toLowerCase())
    console.log(filtrado);
    return filtrado ;
}

//------------------Funcion Icono producto---------------------
function iconoProducto(id) {
    fetch('/api/productosCliente/' + id)
        .then(response => response.json())
        .then(data => {
            document.getElementById(`icono${data.imagen}`).src = data.imagen
        })
} 

function productoSeleccionado(id) {
    localStorage.setItem('productoSeleccionado', id);
}
