var dataTable;
$(document).ready(function() {
     dataTable = $('#compras-table').DataTable({
        "language": {
            url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-CO.json"
        },
        "paging": false,
        "scrollCollapse": true,
        "scrollY": "40vh",
        responsive: true
    });
});

async function detalle(id) {
    try {
        const response = await axios.get('/api/detalles_compra_por_compra/?compra=' + id);
        let data = "";

        // Bucle for...of para asegurar de que las peticiones se completen en orden
        for (const element of response.data) {
            const response3 = await axios.get('/api/productos/' + element.producto);
            const producto = response3.data.nombre;

            data += `<tr>
                <td>${producto}</td>
                <td>${element.cantidad}</td>
                <td>${element.precio_unitario}</td>
            </tr>`;
        }

        datos.innerHTML = data;

        const response2 = await axios.get('/api/compras/' + id);
        const fechaISO8601 = response2.data.fecha_compra;

        const fecha = new Date(fechaISO8601);
        const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' };
        const formattedFecha = fecha.toLocaleString('es-ES', options);

        const response4 = await axios.get('/api/proveedores/' + response2.data.proveedor);
        const proveedor = response4.data.nombre_empresa;

        let data2 = `<p>Fecha de Compra: ${formattedFecha} </p>
                    <p>proveedor: ${proveedor}</p>`;

        contenidoDetalle.innerHTML = data2;
    } catch (e) {
        console.error(e);
    }
}

async function invalidarCompra(id) {
    Swal.fire({
        title: 'Eliminar?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#0d6efd',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si, Eliminarlo!'
    }).then(async (result) => {
        if (result.isConfirmed) {
            const url = '/api/compras/' + id;
            try {
                axios.defaults.xsrfCookieName = 'csrftoken';
                axios.defaults.xsrfHeaderName = 'X-CSRFToken';
                const res = await axios.delete(url);
                Swal.fire(
                    'Borrado!',
                    'Su salida ha sido eliminada.',
                    'success'
                  ).then(result => {
                    if (result.isConfirmed) {
                        location.reload()
                    }
                  })
            } catch (error) {
                console.error(error);
            }
        }
    });
}