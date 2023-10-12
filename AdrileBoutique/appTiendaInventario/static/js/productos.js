// Variales Globales
let id = 0;
let dataTable;
let dataTableIsInitialized = false;

const dataTableOptions = {
    language: {
        url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-CO.json',
    },
    dom: 'Bfrtip',
    buttons: [
        'copy',
        'csv',
        'excel',
        'pdf',
        {
            extend: 'print',
            exportOptions: {
                stripHtml: false,
                columns: [0, 1, 2, 3, 4, 5],
            },
            customize: function(win) {
                // Agregar contenido personalizado al informe de impresión
                const header = '<h1>Mi Informe Personalizado</h1>';
                const table = $('#tuTabla').DataTable();
                const tableHtml = table.table().container().outerHTML;

                $(win.document.body).empty().append(header, tableHtml);
            },
        },
    ],
    columDefs: [
        {className: 'centered', targets: [0, 1, 2, 3, 4]},
        {orderable: false, targets: [5]},
        {searchable: false, targets: [0, 5]},
    ],
    pageLength: 4,
    destroy: true,
    responsive: true,
};

const initDataTable = async () => {
    if (dataTableIsInitialized) {
        dataTable.destroy();
    }
    await getProducts();
    dataTable = $('#tablaProducto').DataTable(dataTableOptions);
    dataTableIsInitialized = true;
};

async function getProducts() {
    try {
        const response = await axios.get('/api/productos/');
        let categorias = JSON.parse(localStorage.categoria);
        let categoryName = '';
        let data = '';
        response.data.forEach((element, index) => {
            categorias.forEach((categoria) => {
                if (categoria.id === element.categoria) {
                    categoryName = categoria.nombre;
                }
            });
            // Formatear el precio con separador de miles y el símbolo COP
            const precioFormateado = new Intl.NumberFormat('es-CO', {
                style: 'currency',
                currency: 'COP',
            }).format(element.precio);
            data += `<tr>
                    <th scope="row">${index + 1}</th>
                    <td>${element.codigo}</td>
                    <td>${element.nombre}</td>
                    <td>${element.descripcion}</td>
                    <td>${element.cantidad_stock}</td>
                    <td>${precioFormateado}</td>
                    <td>${element.talla}</td>
                    <td>${categoryName}</td>
                    <td><img src="${element.imagen}" alt="${element.nombre}" width="100" height="100"></td>
                    <td class="align-middle text-center">
                        <div>
                            <input type="radio" name="checkOpcion" onclick='getProductById(${JSON.stringify(element)})' class="form-check-input" title="Seleccionar">
                        </div> 
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
    formData.append('nombre', txtNombre.value);
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
    formularioData.append('estado', 'true');

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
                timer: 2000,
            });
            getProducts();
            clean();
        } catch (error) {
            listError(error);
        }
    }
}

async function deleteProducts() {
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
    txtCodigo.value="";
    txtTalla.value="";
    txtDescripcion.value = '';
    txtPrecio.value = '';
    cbCategoria.value = 0;
    cbProveedor.value= 0;
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
