// ---------------------Categorias-------------------------------
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
                columns: [0, 1, 2],
            },
        },
    ],
    columnDefs: [
        {
            className: 'centered',
            targets: [0, 1, 2, 3],
        },
        {
            orderable: false,
            targets: [3],
        },
        {
            searchable: false,
            targets: [0, 3],
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
    await listarCat();
    dataTable = $('#tableCat').DataTable(dataTableOptions);
    dataTableIsInitialized = true;
};

async function listarCat() {
    try {
        const response = await axios.get('/api/categorias/');
        let data = '';
        localStorage.categorias = JSON.stringify(response.data);
        console.log(response);
        response.data.forEach((element, index) => {
            const categoriaPadre = obtenerNombreCategoriaPadre(element.categoria_padre);
            data += ` <tr>
                        <th scope="row">${index + 1}</th>
                        <td class="align-middle">${element.nombre}</td>
                        <td>
                            <img src="${element.imagen}" alt="${element.nombre}" width="50" height="50" onclick='vistaImagen("${element.imagen}")'>
                        </td>
                        <td>${categoriaPadre}</td>
                        <td class="align-middle">
                            <input type="radio" name="checkOpcion"  onclick='load(${JSON.stringify(element)})' class="form-check-input">
                        </td>
                    </tr>`;
        });
        tabla.innerHTML = data;
    } catch (error) { }
}

async function agregarCat() {
    axios.defaults.xsrfCookieName = 'csrftoken'; // Nombre de la cookie CSRF
    axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // Nombre del encabezado CSRF;
    var formData = new FormData();
    if (cbCategoriaPadre.selectedIndex > 0) {
        formData.append('categoria_padre', cbCategoriaPadre.value);
    } else {
        console.log('No selecciono Categoria Padre');
    }
    formData.append('nombre', txtNombre.value.trim());
    formData.append('imagen', fileFoto.files[0]);
    try {
        const response = await axios.post('/api/categorias/', formData);
        Swal.fire({
            position: 'center',
            icon: 'success',
            title: 'Categoria agregada correctamente',
            showConfirmButton: true,
            allowOutsideClick: false,
            timer: 2000,
        });
        listarCat();
        limpiar();
    } catch (error) {
        listaErrores(error);
    }
}

async function modificarCat() {
    axios.defaults.xsrfCookieName = 'csrftoken'; // Nombre de la cookie CSRF
    axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // Nombre del encabezado CSRF;
    var formData = new FormData();
    if (cbCategoriaPadre.selectedIndex > 0) {
        formData.append('categoria_padre', cbCategoriaPadre.value);
        if (fileFoto.files.length) {
            formData.append('imagen', fileFoto.files[0]);
        }
    }
    formData.append('nombre', txtNombre.value.trim());
    if ((this.id == undefined && txtNombre.value == '' && !fileFoto.files.length) || this.id == '') {
        Swal.fire({
            position: 'center',
            icon: 'warning',
            title: 'No ha selecionado una categoria para modificar',
            showConfirmButton: true,
            allowOutsideClick: false,
            timer: 1500,
        });
    } else {
        try {
            const response = await axios.put(`/api/categorias/${this.id}/`, formData);
            Swal.fire({
                position: 'center',
                icon: 'success',
                title: 'Categoria Modificada correctamente',
                showConfirmButton: true,
                allowOutsideClick: false,
                timer: 1500,
            });
            await listarCat();
            limpiar();
        } catch (error) {
            listaErrores(error);
        }
    }
}

async function eliminarCat() {
    axios.defaults.xsrfCookieName = 'csrftoken'; // Nombre de la cookie CSRF
    axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // Nombre del encabezado CSRF;
    try {
        const result = await Swal.fire({
            title: 'Eliminar ?',
            text: 'No podras Recuperar esto!',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Si, Borrar!',
        });
        if (result.isConfirmed) {
            if (this.id == '' || this.id == undefined) {
                Swal.fire({
                    position: 'center',
                    icon: 'warning',
                    title: 'No ha selecionado una categoria para eliminar',
                    showConfirmButton: true,
                    allowOutsideClick: false,
                    timer: 1500,
                });
            } else {
                try {
                    const response = await axios.delete(`/api/categorias/${this.id}/`);
                    Swal.fire('Borrado!', 'Su categoria ha sido borrada.', 'success');
                    if (result.isConfirmed) {
                        await listarCat();
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
            html: errorMessageList, // Utilizamos "html" para insertar la lista como HTML
            showConfirmButton: true,
            allowOutsideClick: false,
            timer: 5000,
        });
    }
}

function obtenerNombreCategoriaPadre(idCategoriaPadre) {
    const categorias = JSON.parse(localStorage.categorias);
    const categoria = categorias.find((c) => c.id === idCategoriaPadre);
    return categoria ? categoria.nombre : 'N/A';
}

function obtenerCat() {
    let categorias = JSON.parse(localStorage.categorias);
    console.log(categorias);
    let opcion = `<option value="0">Seleccione categoria padre</option>`;
    categorias.forEach((item) => {
        opcion += `<option value="${item.id}">${item.nombre}</option>`;
    });
    cbCategoriaPadre.innerHTML = opcion;
}

function load(element) {
    this.id = element.id;
    txtNombre.value = element.nombre;
    cbCategoriaPadre.value = element.categoria_padre;
    uploadedImage.src = element.imagen;
    uploadedImage.style.display = 'block';
}

function imagen() {
    const file = fileFoto.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            uploadedImage.src = e.target.result;
            uploadedImage.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        uploadedImage.src = '';
        uploadedImage.style.display = 'none';
    }
}

function vistaImagen(urlFoto) {
    Swal.fire({
        imageUrl: urlFoto,
        imageAlt: 'Custom image',
    });
}

function vistaImagenFrm() {
    url = uploadedImage.src;
    Swal.fire({
        imageUrl: url,
        imageAlt: 'Custom image',
    });
}

function limpiar() {
    this.id = '';
    txtNombre.value = '';
    fileFoto.value = '';
    cbCategoriaPadre.value = 0;
    uploadedImage.style.display = 'none';
    var radioButtons = document.getElementsByName('checkOpcion');
    radioButtons.forEach(function (radioButton) {
        radioButton.checked = false;
    });
}

window.addEventListener('load', async () => {
    await initDataTable();
    obtenerCat();
});
