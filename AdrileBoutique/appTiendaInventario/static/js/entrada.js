var dataTable = ""
$(document).ready(function () {
    // Obtener los datos del localStorage y convertirlos de nuevo a un array
    var productosSeleccionadosJSON = localStorage.getItem('productosSeleccionados');
    productosSeleccionados = JSON.parse(productosSeleccionadosJSON) || [];
    // Actualizar la tabla con los datos restaurados
    actualizarTabla(productosSeleccionados);
    dataTable = $('#productos-seleccionados').DataTable({
        "language": {
            url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-CO.json"
        },
        "paging": false,
        "scrollCollapse": true,
        "scrollY": "40vh",
        responsive: true
    });
});

function pintarDatatable() {
    var table = document.getElementById("productos-seleccionados");
    var dataTable = new DataTable(table, {
        "language": {
            url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-CO.json"
        },
        "paging": false,
        "scrollCollapse": true,
        "scrollY": "40vh",
        responsive: true
    });
}

document.getElementById("cbProveedor").addEventListener("change", function () {
    var selectedProveedorId = this.value;

    var productoSelect = document.getElementById("cbProducto");
    var options = productoSelect.getElementsByTagName("option");

    for (var i = 0; i < options.length; i++) {
        var option = options[i];
        var productoProveedorId = option.getAttribute("data-proveedor");

        if (!selectedProveedorId || selectedProveedorId === productoProveedorId) {
            option.style.display = "block";
        } else {
            option.style.display = "none";
        }
    }
});

// Función actualizarTabla
function actualizarTabla(productos) {
    var tabla = document.getElementById("productos-seleccionados").getElementsByTagName('tbody')[0];
    tabla.innerHTML = "";
    var total = 0;

    productos.forEach(function (producto) {
        var fila = tabla.insertRow(tabla.rows.length);
        var celdaProducto = fila.insertCell(0);
        var celdaPrecioUnitario = fila.insertCell(1);
        var celdaCantidad = fila.insertCell(2);
        var celdaSubtotal = fila.insertCell(3);
        var celdaAcciones = fila.insertCell(4);

        celdaProducto.innerHTML = producto.nombre;
        celdaPrecioUnitario.innerHTML = producto.precio;
        celdaCantidad.innerHTML = producto.cantidad;

        // Agregar un input para la cantidad que permita editarla y tenga un valor mínimo de 1
        var inputCantidad = document.createElement("input");
        inputCantidad.type = "number";
        inputCantidad.value = producto.cantidad;
        inputCantidad.min = 1;
        inputCantidad.addEventListener('change', function () {
            if (inputCantidad.value < 1) {
                inputCantidad.value = 1; // Asegurar que la cantidad mínima sea 1
            }
            producto.cantidad = parseInt(inputCantidad.value);
            localStorage.setItem('productosSeleccionados', JSON.stringify(productos));
            actualizarTabla(productos);
        });
        celdaCantidad.appendChild(inputCantidad);

        var subtotal = producto.precio * producto.cantidad;
        celdaSubtotal.innerHTML = subtotal;
        total += subtotal;

        var eliminarBtn = document.createElement("button");
        eliminarBtn.textContent = "Eliminar";
        eliminarBtn.className = "btn buttons";
        eliminarBtn.addEventListener("click", function () {
            eliminarProducto(producto);
        });
        celdaAcciones.appendChild(eliminarBtn);
    });
    document.getElementById("total").textContent = total;
}

function eliminarProducto(producto) {
    Swal.fire({
        title: '¿Está seguro?',
        text: '¿Desea eliminar este producto de la lista?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            var index = productosSeleccionados.indexOf(producto);
            if (index !== -1) {
                productosSeleccionados.splice(index, 1);
                // Actualizar el localStorage después de eliminar el producto
                localStorage.setItem('productosSeleccionados', JSON.stringify(productosSeleccionados));
                // Recargar la página
                location.reload();
            }
        }
    });
}


var productosSeleccionados = [];
document.getElementById("agregar-producto").addEventListener("click", function () {
    var productoSelect = document.getElementById("cbProducto");
    var cantidadInput = document.getElementById("txtCantidad");
    var precioInput = document.getElementById("txtPrecio");

    var selectedProductoId = productoSelect.value;
    var cantidad = parseInt(cantidadInput.value);
    var precio = parseFloat(precioInput.value);

    if (!selectedProductoId || cantidad < 1 || precio <= 0) {
        Swal.fire({
            icon: 'error',
            title: 'Verifique la información del producto',
            text: 'Asegúrese de que la cantidad sea mayor que 0 y el precio sea válido.',
            showConfirmButton: true,
            timer: 2500
        });
    } else {
        var selectedProductoOption = productoSelect.options[productoSelect.selectedIndex];
        var productoNombre = selectedProductoOption.text;

        productosSeleccionados.push({
            id: selectedProductoId,
            nombre: productoNombre,
            precio: precio,
            cantidad: cantidad,
        });
        localStorage.setItem('productosSeleccionados', JSON.stringify(productosSeleccionados));

        actualizarTabla(productosSeleccionados);
        productoSelect.value = "";
        cantidadInput.value = "";
        precioInput.value = "";
    }
});

$("#crear-entrada").on("click", async function () {
    try {
        // Bloquear el botón durante la petición
        $(this).prop('disabled', true);
        // Realizar la solicitud de compra con los productos seleccionados
        axios.defaults.xsrfCookieName = 'csrftoken';
        axios.defaults.xsrfHeaderName = 'X-CSRFToken';

        var proveedor = $("#cbProveedor").val();
        var detalles = productosSeleccionados.map(function (producto) {
            return {
                producto: producto.id,
                cantidad: producto.cantidad,
                precio_unitario: producto.precio
            };
        });
        if (!proveedor || detalles.length === 0) {
            Swal.fire({
                icon: 'error',
                title: 'Agregue un producto a la tabla para realizar la compras o Entradas.',
                confirmButtonColor: '#0d6efd',
                showConfirmButton: false,
                timer: 1500 // tiempo en milisegundos para que se cierre automáticamente
            });
        } else {
            const response = await axios.post("/api/compras/", { proveedor: proveedor, detalles: detalles });
            Swal.fire({
                icon: 'success',
                title: 'Compra confirmada con éxito.',
                showConfirmButton: true,
                confirmButtonColor: '#0d6efd',
            }).then(result => {
                if (result.isConfirmed) {
                    $("#cbProducto").val("");
                    $("#cbProveedor").val("");
                    $("#txtCantidad").val("");
                    $("#txtPrecio").val("");
                    localStorage.removeItem('productosSeleccionados');
                    productosSeleccionados = [];
                    actualizarTabla(productosSeleccionados);
                    location.href = '/lista_compras/';
                }
            })
        }
    } catch (error) {
        console.error(error);
    } finally {
        // Desbloquear el botón después de la petición, ya sea que haya ocurrido un error o no
        $(this).prop('disabled', false);
    }
});

$("#cancelar-entrada").on("click", function () {
    // Limpiar los campos del formulario
    $("#cbProducto").val("");
    $("#txtCantidad").val("");
    $("#txtPrecio").val("");

    // Limpiar el localStorage
    localStorage.removeItem('productosSeleccionados');

    // Limpiar la tabla
    productosSeleccionados = [];
    actualizarTabla(productosSeleccionados);
    location.href = '/lista_compras/';
});
