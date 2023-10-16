let currentPage = 1; // Página actual
let totalPages = 1; // Número total de páginas

const productosContainer = $('#productosContainer');
const paginationContainer = $('#paginationContainer');

// Función para cargar datos de una página específica
function cargarPagina(page) {
    if (page < 1 || page > totalPages) {
        return; // Evita cargar páginas fuera del rango válido
    }

    // Realiza la petición fetch con el número de página
    fetch(`http://127.0.0.1:8000/api/v1.0/productosPagination/?page=${page}`)
        .then((response) => response.json())
        .then((data) => {
            mostrarResultadosEnHTML(data.results);
            currentPage = page; // Actualiza la página actual
            actualizarPaginacion(data.next, data.previous);
        })
        .catch((error) => {
            console.error('Error al obtener los productos:', error);
        });
}

// Función para mostrar resultados en HTML
function mostrarResultadosEnHTML(resultados) {
    productosContainer.empty(); // Limpia el contenido anterior

    if (resultados.length === 0) {
        productosContainer.html('<p>No se encontraron productos.</p>');
    } else {
        resultados.forEach((producto) => {
            // Crea elementos HTML para mostrar la información del producto
            const productoDiv = $('<div>').addClass('product-card'); // Agrega una clase
            const productoJSON = JSON.stringify(producto); // Serializa el objeto a JSON

            // Formatear el precio con puntos de mil
            const precioConPuntosDeMil = parseFloat(producto.precio).toLocaleString('es-ES', { style: 'currency', currency: 'COP' });

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
                <a class="page-link" href="#productosContainer" onclick="cargarPagina(${currentPage + 1})">Siguien</a>
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
    fetch('http://127.0.0.1:8000/api/v1.0/productosPagination/')
        .then((response) => response.json())
        .then((data) => {
            totalPages = Math.ceil(data.count / 4); // Supongo que estás mostrando 4 productos por página
            cargarPagina(currentPage);
        })
        .catch((error) => {
            console.error('Error al obtener metadatos de paginación:', error);
        });
});