var dataTable; // Define dataTable fuera del alcance de la función para que sea accesible en todo el documento

document.addEventListener("DOMContentLoaded", function () {
    // Inicializa la tabla DataTables
    dataTable = $('#ventas-table').DataTable({
        "language": {
            url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-CO.json"
        },
        "paging": false,
        "scrollCollapse": true,
        "scrollY": "40vh",
        responsive: true
    });
});

async function invalidarVenta(id) {
    Swal.fire({
        title: 'Eliminar?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si, Eliminarlo!'
    }).then(async (result) => {
        if (result.isConfirmed) {
            const url = '/api/ventas/' + id;
            try {
                axios.defaults.xsrfCookieName = 'csrftoken';
                axios.defaults.xsrfHeaderName = 'X-CSRFToken';
                const res = await axios.delete(url);
                console.log(res);
                location.reload()
            } catch (error) {
                console.error(error);
            }
        }
    });
}



async function detalle(id) {
    try {
        const response = await axios.get('/api/detalles_venta_por_venta/?venta=' + id);
        let data = "";

        // Utiliza un bucle for...of para asegurarte de que las peticiones se completen en orden
        for (const element of response.data) {
            const response3 = await axios.get('/api/productos/' + element.producto);
            const producto = response3.data.nombre;

            // Agrega cada detalle a la cadena de datos
            data += `<tr>
                <td>${producto}</td>
                <td>${element.cantidad}</td>
                <td>${element.precio_unitario}</td>
            </tr>`;
        }

        datos.innerHTML = data;

        const response2 = await axios.get('/api/ventas/' + id);
        const fechaISO8601 = response2.data.fecha_venta;

        const fecha = new Date(fechaISO8601);
        const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' };
        const formattedFecha = fecha.toLocaleString('es-CO', options);

        const response4 = await axios.get('/api/clientes/' + response2.data.cliente);
        const cliente = response4.data.nombre;

        let data2 = `<p>Fecha de Venta: ${formattedFecha} </p>
                    <p>Cliente: ${cliente}</p>`;

        contenidoDetalle.innerHTML = data2;
    } catch (e) {
        console.error(e);
    }
}
