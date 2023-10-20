var dataTable = "";
$(document).ready(function () {
    // Obtener los datos del localStorage y convertirlos de nuevo a un array
    var productosSeleccionadosJSON = localStorage.getItem('productosSeleccionadosVenta');
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

let cantidadDisponible = 0
// Solicitud para obtener la lista de productos con Axios.
axios.get('/api/productos/')
    .then(function (response) {
        var products = response.data; // La respuesta contiene un arreglo de objetos de productos.

        // Inicializa el autocompletado en el campo de búsqueda.
        $("#product-search").autocomplete({
            source: products.map(function (product) {
                return product.nombre; // Muestra solo el nombre del producto.
            }),
            select: function (_event, ui) {
                var selectedProduct = ui.item.value; // Obtiene el nombre del producto seleccionado.

                products.forEach(function (product) { //aqui se verifica que sea el producto que que selecionamos para traer sus atributos.
                    if (product.nombre === selectedProduct) {

                        var selectedProductQuantity = product.cantidad_stock;
                        cantidadDisponible = selectedProductQuantity
                        var selectedProductPrice = product.precio;
                        var selectedProductId = product.id;
                        var selectedProductImagen = product.imagen;

                        $("#selected-product").text("Producto seleccionado: " + selectedProduct);
                        $("#available-quantity").text("Cantidad disponible:" + selectedProductQuantity + "UND");
                        $("#imagen").attr("src", selectedProductImagen);

                        // Validación al campo de cantidad.
                        $("#cantidadSalida").attr("max", selectedProductQuantity);

                        // Establece el valor inicial del campo de cantidad en 1.
                        if (selectedProductQuantity < 1) {
                            Swal.fire({
                                icon: 'error',
                                title: 'No hay unidades disponibles',
                                showConfirmButton: false,
                                timer: 1500 // tiempo en milisegundos para que se cierre automáticamente
                            });
                            $("#cantidadSalida").val(0);
                        } else {
                            $("#cantidadSalida").val(1);
                        }

                        // Formatear el precio con separador de miles y el símbolo COP
                        const precioFormateado = new Intl.NumberFormat('es-CO', {
                            style: 'currency',
                            currency: 'COP',
                        }).format(selectedProductPrice);
                        $("#price").val(precioFormateado);
                        $("#productoId").val(selectedProductId);
                    }
                });
            }
        });
    })
    .catch(function (error) {
        console.error("Error al obtener la lista de productos:", error);
    });

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

        var inputCantidad = document.createElement("input");
        inputCantidad.type = "number";
        inputCantidad.value = producto.cantidad;
        inputCantidad.min = 1; // Establecer la cantidad mínima como 1
        inputCantidad.addEventListener('change', function () {
            if (inputCantidad.value < 1) {
                inputCantidad.value = 1; // Asegurar que la cantidad mínima sea 1
            }
            producto.cantidad = parseInt(inputCantidad.value);
            localStorage.setItem('productosSeleccionadosVenta', JSON.stringify(productos));
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
        title: '¿Está seguro de que desea eliminar este producto?',
        text: "Esta acción no se puede deshacer.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar'
    }).then((result) => {
        if (result.isConfirmed) {
            var index = productosSeleccionados.findIndex(item => item.id === producto.id);
            if (index !== -1) {
                productosSeleccionados.splice(index, 1);
                // Actualizar la tabla después de eliminar el producto
                localStorage.setItem('productosSeleccionadosVenta', JSON.stringify(productosSeleccionados));
                Swal.fire(
                    'Eliminado',
                    'El producto ha sido eliminado correctamente.',
                    'success'
                ).then(() => {
                    location.reload(); // Recargar la página después de eliminar el producto
                });
            }
        }
    });
}



var productosSeleccionados = [];
document.getElementById("agregar-producto").addEventListener("click", function () {
    var productoSelect = document.getElementById("productoId");
    var cantidadInput = document.getElementById("cantidadSalida");
    var precioInput = document.getElementById("price");
    var productoNombre = document.getElementById("product-search");

    var selectedProductoId = productoSelect.value;
    var nombre = productoNombre.value;
    var cantidad = parseInt(cantidadInput.value);
    var precio = precioInput.value;
    const valorNumerico = desformatearValor(precio);

    if (!selectedProductoId || cantidad === 0 || precio === "") {
        Swal.fire({
            icon: 'error',
            title: 'Elija un producto',
            showConfirmButton: true,
            timer: 2500
        });
    } else {
        if (cantidadDisponible < cantidad) {
            Swal.fire({
                icon: 'error',
                title: 'NO hay suficientes productos disponibles',
                showConfirmButton: true,
                timer: 2500
            });
        } else {
            // Verificar si el producto ya existe en la lista
            var productoExistente = productosSeleccionados.find(item => item.id === selectedProductoId);
            if (productoExistente) {
                productoExistente.cantidad += cantidad; // Actualiza la cantidad existente
            } else {
                productosSeleccionados.push({
                    id: selectedProductoId,
                    nombre: nombre,
                    precio: valorNumerico,
                    cantidad: cantidad,
                });
            }
            localStorage.setItem('productosSeleccionadosVenta', JSON.stringify(productosSeleccionados));

            actualizarTabla(productosSeleccionados);
            limpiar();
        }
    }
});


function desformatearValor(valorFormateado) {
    const soloNumeros = valorFormateado.replace(/[^\d.]/g, ''); // Elimina todo excepto números y puntos decimales
    const valorNumerico = parseFloat(soloNumeros) * 1000;
    return valorNumerico;
}

function limpiar() {
    var productoSelect = document.getElementById("productoId");
    var cantidadInput = document.getElementById("cantidadSalida");
    var precioInput = document.getElementById("price");
    var productoNombre = document.getElementById("product-search")

    productoSelect.value = "";
    cantidadInput.value = "";
    precioInput.value = "";
    productoNombre.value = "";
    $("#imagen").attr("src", "");
}

document.getElementById("realizar-venta").addEventListener("click", function () {
    // Deshabilitar el botón al hacer la petición
    var realizarVentaBtn = document.getElementById("realizar-venta");
    realizarVentaBtn.disabled = true;

    // Token que permite hacer solicitudes post a la Api
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';

    var cliente = document.getElementById("cbCliente").value;
    var detalles = productosSeleccionados.map(function (producto) {
        return {
            producto: producto.id,
            cantidad: producto.cantidad,
            precio_unitario: producto.precio,
        };
    });

    if (!cliente || !detalles) {
        Swal.fire({
            icon: 'error',
            title: 'Agregue un producto a la tabla para realizar la venta o salida.',
            showConfirmButton: false,
            confirmButtonColor: '#0d6efd',
            timer: 1500 // tiempo en milisegundos para que se cierre automáticamente
        });
        // Habilitar el botón en caso de error
        realizarVentaBtn.disabled = false;
    } else {
        axios.post("/api/ventas/", { cliente: cliente, detalles: detalles })
            .then(function (response) {
                Swal.fire({
                    icon: 'success',
                    title: 'Venta realizada con éxito.',
                    confirmButtonColor: '#0d6efd',
                    showConfirmButton: true,
                }).then((result) => {
                    if (result.isConfirmed) {
                        limpiar()
                        localStorage.removeItem('productosSeleccionadosVenta');
                        productosSeleccionados = [];
                        actualizarTabla(productosSeleccionados);
                        location.href = '/lista_ventas/';
                    }
                });
            })
            .catch(function (error) {
                console.error(error);
            })
            .finally(function () {
                // Habilitar el botón después de la respuesta, ya sea éxito o error
                realizarVentaBtn.disabled = false;
            });
    }
});


document.getElementById("cancelar-salida").addEventListener("click", function () {
    limpiar()

    // Limpiar el localStorage
    localStorage.removeItem('productosSeleccionadosVenta');

    // Limpiar la tabla
    productosSeleccionados = []; // Limpiar productos seleccionados
    actualizarTabla(productosSeleccionados);

    // Cambiar la redirección si es necesario
    location.href = '/lista_ventas/';
});
