const id = localStorage.getItem('productoSelecionado')

// Obtener el ID del producto desde la URL
const urlParams = new URLSearchParams(window.location.search);
const idProducto = urlParams.get('id');

if (idProducto) {
    // solicitud GET al servidor con el ID incluido en la URL
    fetch(`http://127.0.0.1:8000/api/v1.0/productosCliente/${idProducto}`)
        .then((response) => {
            if (response.ok) {
                console.log(response)
                return response.json();
            } else {
                throw new Error('No se pudo obtener el producto');
            }
        })
        .then((producto) => {
            const detallesProductoElement = document.getElementById('detallesProducto');

            // Formatear el precio con puntos de mil
            const precioConPuntosDeMil = parseFloat(producto.precio).toLocaleString('es-ES', { style: 'currency', currency: 'COP' });

            detallesProductoElement.innerHTML = `
            <h3 class="text-center border border-warning" style="margin: 50px;">Detalles De ${producto.nombre}</h3>
                <div class="row">
                    <div class="col-md-8">
                        <img src="${producto.imagen}" alt="${producto.nombre}" class="img-fluid rounded" style="max-width: 100%; height: 400px;" />
                    </div>
                    <div class="col-md-4 card shadow" style="height: 400px;">
                            <div class="card-body">
                                <h3 class="card-title text-primary">${producto.nombre}</h3>
                                <p class="card-text">
                                    <strong>Precio:</strong> ${precioConPuntosDeMil}
                                </p>
                                <p class="card-text">
                                    <strong>Descripción:</strong> ${producto.descripcion}
                                </p>
                                <button class="btn btn-warning">Comprar Ahora</button>
                            </div>
                    </div>
                </div>
            `;
        })
        .catch((error) => {
            console.error('Error al obtener los detalles del producto', error);
        });
} else {
    console.error('No se encontró el ID del producto en la URL');
}
