let dataTable;
let dataTableIsInitialized = false;
let id = 0;

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
                columns: [0, 1, 2, 3, 4, 5, 6, 7, 8],
            },
        },
    ],
    columnDefs: [
        {
            className: 'centered',
            targets: [0, 1, 2, 3, 4, 5, 6, 7, 8],
        },
        {
            orderable: false,
            targets: [8],
        },
        {
            searchable: false,
            targets: [0, 8],
        },
    ],
    pageLength: 10,
    destroy: true,
    responsive: true,
};

const initDataTable = async () => {
    if (dataTableIsInitialized) {
        dataTable.destroy();
    }
    await listarProveedores();
    dataTable = $('#tablaProveedor').DataTable(dataTableOptions);
    dataTableIsInitialized = true;
};

async function listarProveedores() {
    try {
        const response = await axios.get('/api/proveedores/');
        let data = '';
        localStorage.proveedores = JSON.stringify(response.data);
        console.log(response);
        response.data.forEach((element, index) => {
            data += ` <tr>
                        <th scope="row">${index + 1}</th>
                        <td class="align-middle">${element.nombre_empresa}</td>
                        <td class="align-middle">${element.nombre_contacto}</td>
                        <td class="align-middle">${element.direccion}</td>
                        <td class="align-middle">${element.telefono}</td>
                        <td class="align-middle">${element.correo_electronico}</td>
                        <td class="align-middle">${element.notas}</td>
                        <td class="align-middle">${element.fecha_creacion}</td>
                        <td class="align-middle">${element.fecha_actualizacion}</td>
                        <td class="align-middle">
                            <input type="radio" name="checkOpcion" onclick='load(${JSON.stringify(element)})' class="form-check-input">
                        </td>
                    </tr>`;
        });
        tablaContent.innerHTML = data;
    } catch (error) { }
}

async function agregarProveedor() {
    axios.defaults.xsrfCookieName = 'csrftoken'; // Nombre de la cookie CSRF
    axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // Nombre del encabezado CSRF
    var formData = new FormData();
    formData.append('nombre_empresa', txtNombreEmpresa.value.trim());
    formData.append('nombre_contacto', txtNombreContacto.value.trim());
    formData.append('direccion', txtDireccion.value.trim());
    formData.append('telefono', txtTelefono.value.trim());
    formData.append('correo_electronico', txtCorreoElectronico.value.trim());
    formData.append('notas', txtNotas.value.trim());
    try {
        const response = await axios.post('/api/proveedores/', formData);
        Swal.fire({
            position: 'center',
            icon: 'success',
            title: 'Proveedor agregado correctamente',
            showConfirmButton: true,
            allowOutsideClick: false,
            timer: 2000,
        });
        listarProveedores();
        limpiar();
    } catch (error) {
        listaErrores(error);
    }
}

async function modificarProveedor() {
    axios.defaults.xsrfCookieName = 'csrftoken'; // Nombre de la cookie CSRF
    axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // Nombre del encabezado CSRF
    var formData = new FormData();
    formData.append('nombre_empresa', txtNombreEmpresa.value.trim());
    formData.append('nombre_contacto', txtNombreContacto.value.trim());
    formData.append('direccion', txtDireccion.value.trim());
    formData.append('telefono', txtTelefono.value.trim());
    formData.append('correo_electronico', txtCorreoElectronico.value.trim());
    formData.append('notas', txtNotas.value.trim());
    if (id === 0) {
        Swal.fire({
            position: 'center',
            icon: 'warning',
            title: 'No ha seleccionado un proveedor para modificar',
            showConfirmButton: true,
            allowOutsideClick: false,
            timer: 1500,
        });
    } else {
        try {
            const response = await axios.put(`/api/proveedores/${id}/`, formData);
            Swal.fire({
                position: 'center',
                icon: 'success',
                title: 'Proveedor modificado correctamente',
                showConfirmButton: true,
                allowOutsideClick: false,
                timer: 1500,
            });
            await listarProveedores();
            limpiar();
        } catch (error) {
            listaErrores(error);
        }
    }
}

async function eliminarProveedor() {
    axios.defaults.xsrfCookieName = 'csrftoken'; // Nombre de la cookie CSRF
    axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // Nombre del encabezado CSRF
    try {
        const result = await Swal.fire({
            title: 'Eliminar?',
            text: 'No podrás recuperar esto!',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, Borrar!',
        });
        if (result.isConfirmed) {
            if (id === 0) {
                Swal.fire({
                    position: 'center',
                    icon: 'warning',
                    title: 'No ha seleccionado un proveedor para eliminar',
                    showConfirmButton: true,
                    allowOutsideClick: false,
                    timer: 1500,
                });
            } else {
                try {
                    const response = await axios.delete(`/api/proveedores/${id}/`);
                    Swal.fire('Borrado!', 'El proveedor ha sido borrado.', 'success');
                    if (result.isConfirmed) {
                        await listarProveedores();
                        limpiar();
                    }
                } catch (error) {
                    listaErrores(error.response.data);
                }
            }
        }
    } catch (error) { }
}

function listaErrores(error) {
    var errorMessages = [];
    for (var key in error.response.data) {
        if (error.response.data.hasOwnProperty(key)) {
            var mensajes = error.response.data[key];
            if (typeof mensajes === 'string') {
                errorMessages.push(mensajes);
            } else if (mensajes instanceof Array) {
                for (var i = 0; i = errorMessages.length; j++) {
                    errorMessageList += '<li class="list-group-item">' + errorMessages[j] + '</li>';
                }
                errorMessageList += '</ul>';
                Swal.fire({
                    position: 'center',
                    icon: 'error',
                    title: 'Oops...',
                    html: errorMessageList, // Utilizamos "html" para insertar la lista como HTML
                    showConfirmButton: true,
                    allowOutsideClick: false,
                    timer: 5000,
                });
            }
        }
    }
}

function load(element) {
    this.id = element.id;
    txtNombreEmpresa.value = element.nombre_empresa;
    txtNombreContacto.value = element.nombre_contacto;
    txtDireccion.value = element.direccion;
    txtTelefono.value = element.telefono;
    txtCorreoElectronico.value = element.correo_electronico;
    txtNotas.value = element.notas;
}

function limpiar() {
    this.id = 0;
    txtNombreEmpresa.value = '';
    txtNombreContacto.value = '';
    txtDireccion.value = '';
    txtTelefono.value = '';
    txtCorreoElectronico.value = '';
    txtNotas.value = '';
    var radioButtons = document.getElementsByName('checkOpcion');
    radioButtons.forEach(function (radioButton) {
        radioButton.checked = false;
    });
}

window.addEventListener('load', async () => {
    await initDataTable();
});
