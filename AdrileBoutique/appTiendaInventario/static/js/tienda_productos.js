var currentPage = 1; // Página actual
var totalPages = 1; // Número total de páginas

var productosContainer = $('#productosContainer');
var paginationContainer = $('#paginationContainer');

// Función para cargar datos de una página específica
function cargarPagina(page) {
    if (page < 1 || page > totalPages) {
        return; // Evita cargar páginas fuera del rango válido
    }
    const reversePage = totalPages - page + 1;

    // Realiza la petición fetch con el número de página
    axios.get(`/api/productosPagination/?page=${reversePage}`)
        .then((response) => {
            const resultadosInvertidos = response.data.results.reverse();
            mostrarResultadosEnHTML(resultadosInvertidos);
            currentPage = page; // Actualiza la página actual
            actualizarPaginacion(response.data.next, response.data.previous);
        })
        .catch((error) => {
            console.error('Error al obtener los productos:', error);
        });
}


// Función para cargar y mostrar los últimos 12 productos en la sección de la cuadrícula
// function mostrarUltimosProductos(resultados) {
//     const ultimosProductosSection = $('.ultimos-productos-section .row');
//     ultimosProductosSection.empty();

//     // Iterar sobre los últimos 12 productos
//     const ultimosDoceProductos = resultados.slice(-12);
//     ultimosDoceProductos.forEach((producto) => {
//         const precioConPuntosDeMil = parseFloat(producto.precio).toLocaleString('es-ES', { style: 'currency', currency: 'COP' });

//         const productoCard = `
//             <div class="col-md-3">
//                 <div class="producto-card">
//                     <a href="/detalle_producto?id=${producto.id}" onclick="productoSeleccionado(${producto.id})">
//                         <h3 class="product-name">${producto.nombre}</h3>
//                         <p>Precio: ${precioConPuntosDeMil}</p>
//                         <img src="${producto.imagen}" alt="${producto.nombre}" class="img-fluid">
//                     </a>
//                 </div>
//             </div>
//         `;

//         ultimosProductosSection.append(productoCard);
//     });
// }



// function mostrarEnCarrusel(resultados) {
//     productosContainer.empty();
//     const carruselInner = $('<div>').addClass('carousel-inner');

//     resultados.forEach((producto, index) => {
//         const activeClass = index === 0 ? 'active' : '';
//         const precioConPuntosDeMil = parseFloat(producto.precio).toLocaleString('es-ES', {
//             style: 'currency',
//             currency: 'COP'
//         });
//         const item = `
//             <div class="carousel-item ${activeClass}">
//                 <a class="linkCard" href="/detalle_producto?id=${producto.id}" onclick="productoSeleccionado(${producto.id})">
//                     <h3 class="product-name">${producto.nombre}</h3>
//                     <p>Precio: ${precioConPuntosDeMil}</p>
//                     <img src="${producto.imagen}" alt="${producto.nombre}" style="max-width: 100%; height: 250px;" class="rounded" />
//                 </a>
//             </div>
//         `;
//         carruselInner.append(item);
//     });

//     const carrusel = $('<div>').addClass('carousel slide').attr('data-ride', 'carousel');
//     carrusel.append(carruselInner);

//     productosContainer.append(carrusel);
// }

function mostrarDeAtrasHaciaAdelante(resultados) {
    productosContainer.empty();
    resultados.reverse(); // Revierte el orden de los resultados

    resultados.forEach((producto) => {
        const productoDiv = $('<div>').addClass('product-card');
        const productoJSON = JSON.stringify(producto);

        const precioConPuntosDeMil = parseFloat(producto.precio).toLocaleString('es-ES', {
            style: 'currency',
            currency: 'COP'
        });

        productoDiv.html(`
            <a class="linkCard" href="/detalle_producto?id=${producto.id}" onclick="productoSeleccionado(${producto.id})">
            <h3 class="product-name">${producto.nombre}</h3>
            <p>Precio: ${precioConPuntosDeMil}</p>
            <img src="${producto.imagen}" alt="${producto.nombre}" style="max-width: 100%; height: 250px;" class="rounded" />
            </a>
        `);
        productosContainer.append(productoDiv);
    });
}

// Función para mostrar resultados en HTML
function mostrarResultadosEnHTML(resultados) {
    productosContainer.empty(); // Limpia el contenido anterior
    //mostrarEnCarrusel(resultados);

    if (resultados.length === 0) {
        productosContainer.html('<p>No se encontraron productos.</p>');
    } else {
        resultados.forEach((producto) => {
            // Crea elementos HTML para mostrar la información del producto
            const productoDiv = $('<div>').addClass('product-card'); // Agrega una clase
            const productoJSON = JSON.stringify(producto); // Serializa el objeto a JSON

            // Formatear el precio con puntos de mil
            const precioConPuntosDeMil = parseFloat(producto.precio).toLocaleString('es-ES', {
                style: 'currency',
                currency: 'COP'
            });

            productoDiv.html(`
                <a class="linkCard" href="/detalle_producto?id=${producto.id}" onclick="productoSeleccionado(${producto.id})">
                <h3 class="product-name">${producto.nombre}</h3>
                <p>Precio: ${precioConPuntosDeMil}</p>
                <img src="${producto.imagen}" alt="${producto.nombre}" style="max-width: 100%; height: 250px;" class="rounded" />
                </a>
            `);
            productosContainer.append(productoDiv);
        });
    }
}

// Función para actualizar la paginación
function actualizarPaginacion(nextPageUrl, prevPageUrl) {
    paginationContainer.empty(); // Limpia la paginación existente

    const pagination = `
    <nav aria-label="Page navigation example">
        <ul class="pagination">
            <li class="page-item ${prevPageUrl ? '' : 'disabled'}">
                <a class="page-link" href="#productosContainer" onclick="cargarPagina(${currentPage - 1})">Anterior</a>
            </li>
            ${generarEnlacesPagina(currentPage, totalPages)}
            <li class="page-item ${nextPageUrl ? '' : 'disabled'}">
                <a class="page-link" href="#productosContainer" onclick="cargarPagina(${currentPage + 1})">Siguiente</a>
            </li>
        </ul>
    </nav>
    `;
    paginationContainer.html(pagination);
}

// Función para generar enlaces de página individuales
function generarEnlacesPagina(currentPage, totalPages) {
    let pageLinks = '';

    for (let page = 1; page <= totalPages; page++) {
        const activeClass = currentPage === page ? 'active' : '';
        pageLinks += `
            <li class="page-item ${activeClass}">
                <a class="page-link" href="#productosContainer" onclick="cargarPagina(${page})">${page}</a>
            </li>
        `;
    }

    return pageLinks;
}


// Evento para cargar la primera página al cargar la página web (sirve bien si el Script esta al final del html)
$(document).ready(() => {
    // Realiza la petición fetch para obtener el número total de páginas
    fetch('/api/productosPagination/')
        .then((response) => response.json())
        .then((data) => {
            totalPages = Math.ceil(data.count / 4); //4 productos por página
            cargarPagina(currentPage);
        })
        .catch((error) => {
            console.error('Error al obtener metadatos de paginación:', error);
        });
});

// obtenerUltimosProductos()