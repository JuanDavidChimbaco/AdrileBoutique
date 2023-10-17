// Variales Globales
let id = 0;
let dataTable;
let dataTableIsInitialized = false;

const dataTableOptions = {
    language: {
        url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-CO.json',
    },
    paging: false,
    scrollCollapse: true,
    scrollY: "40vh",
    dom: 'Bfrtip',
    buttons: [
        {
            extend:'copy',
            text: '<i class="fa-solid fa-copy"></i>',
            exportOptions: {
                stripHtml: false,
                columns: [0, 1, 2, 3, 4],
            },
        },
        {
            extend:'csv',
            text: '<i class="fa-solid fa-file-csv"></i>',
            exportOptions: {
                stripHtml: false,
                columns: [0, 1, 2, 3, 4],
            },
        },
        {
            extend:'excel',
            text: '<i class="fa-solid fa-file-excel"></i>',
            exportOptions: {
                stripHtml: false,
                columns: [0, 1, 2, 3, 4],
            },
        },
        {
            extend:'pdf',
            text: '<i class="fa-solid fa-file-pdf"></i>',
            exportOptions: {
                stripHtml: false,
                columns: [0, 1, 2, 3, 4],
            },
        },
        {
            extend: 'print',
            text: '<i class="fa-solid fa-print"></i>',
            exportOptions: {
                stripHtml: false,
                columns: [0, 1, 2, 3, 4],
            },
        },
    ],
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4] },
        { orderable: false, targets: [5] },
        { searchable: false, targets: [0, 5] },
    ],
    // pageLength: 4,
    destroy: true,
    responsive: true,
};

const initDataTable = async () => {
    if (dataTableIsInitialized) {
        dataTable.destroy();
    }
    await getProducts();
    dataTable = $('#tablaProducto').DataTable(dataTableOptions).columns.adjust();;
    dataTableIsInitialized = true;
};

async function getProducts() {
    try {
        const response = await axios.get('/api/productos/');
        let data = '';
        response.data.forEach((element, index) => {
            // Formatear el precio con separador de miles y el símbolo COP
            const precioFormateado = new Intl.NumberFormat('es-CO', {
                style: 'currency',
                currency: 'COP',
            }).format(element.precio);
            data += `<tr>
                    <th scope="row">${index + 1}</th>
                    <td>${element.codigo}</td>
                    <td>${element.nombre}</td>
                    <td>${element.cantidad_stock}</td>
                    <td>${precioFormateado}</td>
                    <td>
                        <a type="button" onclick='getProductById(${JSON.stringify(element)})' title="Ver Producto" data-bs-toggle="modal" data-bs-target="#staticBackdrop"><i class="fa-solid fa-eye"></i></a>
                        <a type="button" onclick="deleteProducts(${element.id})" title="Eliminar Producto"><i class="fa-solid fa-trash"></i></a>
                    </td>
                </tr>`;
        });
        tablaContent.innerHTML = data;
    } catch (error) {
        console.error(error);
    }
}

async function addProducts() {
    axios.defaults.xsrfCookieName = 'csrftoken'; // Nombre de la cookie CSRF
    axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // Nombre del encabezado CSRF
    var formData = new FormData();
    formData.append('codigo', txtCodigo.value);
    formData.append('nombre', txtNombre.value.toLowerCase());
    formData.append('descripcion', txtDescripcion.value);
    formData.append('precio', txtPrecio.value);
    formData.append('imagen', fileFoto.files[0]);
    formData.append('estado', 'True');
    formData.append('talla', txtTalla.value);
    formData.append('categoria', cbCategoria.value);
    formData.append('cantidad_stock', 0);
    formData.append('proveedor', cbProveedor.value);
    if (emptyFields()) {
        Swal.fire({
            position: 'center',
            icon: 'warning',
            title: 'Hay campos vacios',
            showConfirmButton: true,
            allowOutsideClick: false,
            timer: 1500,
        });
    } else {
        try {
            const response = await axios.post('/api/productos/', formData);
            Swal.fire({
                position: 'center',
                icon: 'success',
                title: 'Producto agregado correctamente',
                showConfirmButton: true,
                allowOutsideClick: false,
                timer: 2000,
            });
            getProducts();
            clean();
        } catch (error) {
            listError(error);
        }
    }
}

async function modifyProducts() {
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    var formularioData = new FormData();
    if (fileFoto.files.length) {
        formularioData.append('imagen', fileFoto.files[0]);
    }
    formularioData.append('nombre', txtNombre.value);
    formularioData.append('descripcion', txtDescripcion.value);
    formularioData.append('precio', txtPrecio.value);
    formularioData.append('categoria', cbCategoria.value);
    formularioData.append('estado', 'True');

    formularioData.append('codigo', txtCodigo.value);
    formularioData.append('talla', txtTalla.value);
    formularioData.append('categoria', cbCategoria.value);
    formularioData.append('cantidad_stock', 0);
    formularioData.append('proveedor', cbProveedor.value);

    if (emptyFields()) {
        Swal.fire({
            position: 'center',
            icon: 'warning',
            title: 'Hay campos vacios',
            showConfirmButton: true,
            allowOutsideClick: false,
            timer: 1500,
        });
    } else {
        try {
            const response = await axios.put(`/api/productos/${this.id}/`, formularioData);
            Swal.fire({
                position: 'center',
                icon: 'success',
                title: 'Producto Modificado correctamente',
                showConfirmButton: true,
                allowOutsideClick: false,
                confirmButtonColor: '#0d6efd',
            });
            $('#staticBackdrop').modal('hide');
            clean();
            getProducts();
        } catch (error) {
            listError(error);
        }
    }
}

async function deleteProducts(id) {
    this.id = id
    axios.defaults.xsrfCookieName = 'csrftoken'; // Nombre de la cookie CSRF
    axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // Nombre del encabezado CSRF
    const res = await Swal.fire({
        title: 'Desea Eliminar el Producto?',
        text: 'Si lo haces no se podra Revertir!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si, Eliminarlo!',
    });
    if (res.isConfirmed) {
        if (this.id === '' || this.id === undefined || this.id === 0) {
            Swal.fire({
                position: 'center',
                icon: 'warning',
                title: 'No ha selecionado un producto para eliminar',
                showConfirmButton: true,
                allowOutsideClick: false,
                timer: 1500,
            });
        } else {
            try {
                const response = await axios.delete(`/api/productos/${this.id}/`);
                Swal.fire('Borrado!', 'Su producto ha sido borrado.', 'success');
                getProducts();
                clean();
            } catch (error) {
                listError(error);
            }
        }
    }
}

function getProductById(element) {
    this.id = element.id;
    console.log(element);
    txtCodigo.value = element.codigo;
    txtTalla.value = element.talla;
    txtNombre.value = element.nombre;
    txtDescripcion.value = element.descripcion;
    txtPrecio.value = element.precio;
    cbCategoria.value = element.categoria;
    cbProveedor.value = element.proveedor;
    vistaPrevia.src = element.imagen;
    vistaPrevia.style.display = 'block';
}

function view() {
    const file = fileFoto.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            vistaPrevia.src = e.target.result;
            vistaPrevia.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        vistaPrevia.src = e.target.result;
        vistaPrevia.style.display = 'none';
    }
}

function listError(error) {
    var errorMessages = [];
    for (var key in error.response.data) {
        if (error.response.data.hasOwnProperty(key)) {
            var mensajes = error.response.data[key];
            if (typeof mensajes === 'string') {
                errorMessages.push(mensajes);
            } else if (mensajes instanceof Array) {
                for (var i = 0; i < mensajes.length; i++) {
                    errorMessages.push(mensajes[i]);
                }
            }
        }
    }
    if (errorMessages.length > 0) {
        var errorMessageList = '<ul class="list-group list-group-numbered">';
        for (var j = 0; j < errorMessages.length; j++) {
            errorMessageList += '<li class="list-group-item">' + errorMessages[j] + '</li>';
        }
        errorMessageList += '</ul>';
        Swal.fire({
            position: 'center',
            icon: 'error',
            title: 'Oops...',
            html: errorMessageList,
            showConfirmButton: true,
            allowOutsideClick: false,
            timer: 5000,
        });
    }
}

function viewImageFrm() {
    url = vistaPrevia.src;
    Swal.fire({
        imageUrl: url,
        imageAlt: 'Custom image',
    });
}

function emptyFields() {
    if (txtNombre.value === '' || txtDescripcion.value === '' || txtPrecio.value === '' || (cbCategoria.value === 0 && !fileFoto.files.length)) {
        return true;
    } else {
        return false;
    }
}

function clean() {
    this.id = '';
    txtNombre.value = '';
    txtCodigo.value = "";
    txtTalla.value = "";
    txtDescripcion.value = '';
    txtPrecio.value = '';
    cbCategoria.value = 0;
    cbProveedor.value = 0;
    fileFoto.value = '';
    vistaPrevia.style.display = 'none';
    var radioButtons = document.getElementsByName('checkOpcion');
    radioButtons.forEach(function (radioButton) {
        radioButton.checked = false;
    });
}

window.addEventListener('load', async () => {
    await initDataTable();
});
