function configCarousel() {
    const myCarouselElement = document.querySelector('#carouselExampleAutoplaying');

    const carousel = new bootstrap.Carousel(myCarouselElement, {
        interval: 2000,
        touch: false
    });
}

async function ultimosProductos(){
    try {
        url = '/api/v1.0/categoriaCliente'
        const response = await axios.get(url)
        const categorias = response.data;

        // Obtén la referencia al elemento del carrusel
        const carouselInner = document.querySelector('.carousel-inner');

        // Recorre las categorías y crea elementos de imagen para cada una
        categorias.forEach((categoria, index) => {
            const carouselItem = document.createElement('div');
            carouselItem.classList.add('carousel-item');

            const imgContainer = document.createElement('div');
            imgContainer.classList.add('d-flex', 'w-100', 'justify-content-center');

            const img = document.createElement('img');
            img.src = categoria.imagen; // Asume que la categoría tiene una propiedad "imagen_url"
            img.classList.add('rounded', 'img-fluid', 'categoria-imagen');
            img.alt = `Imagen de ${categoria.nombre}`; // Asume que la categoría tiene una propiedad "nombre"

            imgContainer.appendChild(img);
            carouselItem.appendChild(imgContainer);

            if (index === 0) {
                carouselItem.classList.add('active');
            }

            // carouselInner.appendChild(carouselItem);
        });

        console.log('categorias', categorias);
    } catch (error) {
        console.error(error);
    }
}
window.onload = () => {
    configCarousel();
    ultimosProductos();
};