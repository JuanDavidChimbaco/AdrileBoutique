document.addEventListener('DOMContentLoaded', function () {
    // Obtener los datos del localStorage y convertirlos de nuevo a un array
    var productosSeleccionadosJSON = localStorage.getItem('productosSeleccionados');
    productosSeleccionados = JSON.parse(productosSeleccionadosJSON) || [];

    // Actualizar la tabla con los datos restaurados
    actualizarTabla();
});


document.getElementById("cancelar-entrada").addEventListener("click", function () {
    // Limpiar los campos del formulario
    var productoSelect = document.getElementById("cbProducto");
    var cantidadInput = document.getElementById("txtCantidad");
    var precioInput = document.getElementById("txtPrecio");

    productoSelect.value = "";
    cantidadInput.value = "";
    precioInput.value = "";

    // Limpiar el localStorage
    localStorage.removeItem('productosSeleccionados');

    // Limpiar la tabla
    productosSeleccionados = [];
    actualizarTabla();
    location.href = '/lista_compras/'
});


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

var productosSeleccionados = [];

function actualizarTabla() {
    var tabla = document.getElementById("productos-seleccionados").getElementsByTagName('tbody')[0];
    tabla.innerHTML = "";

    var total = 0;

    productosSeleccionados.forEach(function (producto) {
        var fila = tabla.insertRow(tabla.rows.length);
        var celdaProducto = fila.insertCell(0);
        var celdaPrecioUnitario = fila.insertCell(1);
        var celdaCantidad = fila.insertCell(2);
        var celdaSubtotal = fila.insertCell(3);
        var celdaAcciones = fila.insertCell(4);

        celdaProducto.innerHTML = producto.nombre;
        celdaPrecioUnitario.innerHTML = producto.precio;
        celdaCantidad.innerHTML = producto.cantidad;

        var subtotal = producto.precio * producto.cantidad;
        celdaSubtotal.innerHTML = subtotal;
        total += subtotal;

        var eliminarBtn = document.createElement("button");
        eliminarBtn.textContent = "Eliminar";
        eliminarBtn.addEventListener("click", function () {
            eliminarProducto(producto);
        });
        celdaAcciones.appendChild(eliminarBtn);
    });

    document.getElementById("total").textContent = total;
}

function eliminarProducto(producto) {
    var index = productosSeleccionados.indexOf(producto);
    if (index !== -1) {
        productosSeleccionados.splice(index, 1);
        actualizarTabla();
    }
}

document.getElementById("agregar-producto").addEventListener("click", function () {
    var productoSelect = document.getElementById("cbProducto");
    var cantidadInput = document.getElementById("txtCantidad");
    var precioInput = document.getElementById("txtPrecio");

    var selectedProductoId = productoSelect.value;
    var cantidad = parseInt(cantidadInput.value);
    var precio = parseFloat(precioInput.value);

    if (selectedProductoId && cantidad > 0 && precio > 0) {
        var selectedProductoOption = productoSelect.options[productoSelect.selectedIndex];
        var productoNombre = selectedProductoOption.text;

        productosSeleccionados.push({
            id: selectedProductoId,
            nombre: productoNombre,
            precio: precio,
            cantidad: cantidad,
        });

        localStorage.setItem('productosSeleccionados', JSON.stringify(productosSeleccionados));

        actualizarTabla();
        productoSelect.value = "";
        cantidadInput.value = "";
        precioInput.value = "";
    }
});

document.getElementById("crear-entrada").addEventListener("click", function () {
    // Realizar la solicitud de compra con los productos seleccionados
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';

    var proveedor = document.getElementById("cbProveedor").value;
    var detalles = productosSeleccionados.map(function (producto) {
        return {
            producto: producto.id,
            cantidad: producto.cantidad,
            precio_unitario: producto.precio,
        };
    });

    axios.post("/api/compras/", {
        proveedor: proveedor,
        detalles: detalles
    })
        .then(function (response) {
            console.log(response.data);
            Swal.fire({
                icon: 'success',
                title: 'Compra confirmada con éxito.',
                showConfirmButton: false,
                timer: 1500 // tiempo en milisegundos para que se cierre automáticamente
            });
            
            var productoSelect = document.getElementById("cbProducto");
            var cantidadInput = document.getElementById("txtCantidad");
            var precioInput = document.getElementById("txtPrecio");

            productoSelect.value = "";
            cantidadInput.value = "";
            precioInput.value = "";

            // Limpiar el localStorage
            localStorage.removeItem('productosSeleccionados');

            // Limpiar la tabla
            productosSeleccionados = []; // Limpiar productos seleccionados
            actualizarTabla();
            location.href = '/lista_compras/';
        })
        .catch(function (error) {
            console.error(error);
        });

});