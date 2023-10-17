$(window).on('load', function() {
  var loaderWrapper = $('.loader-wrapper');
  loaderWrapper.css('display', 'none');
});

function mostrarImagen(evento){
    const archivos = evento.target.files
    const archivo = archivos[0]
    const url = URL.createObjectURL(archivo)  
    $("#imagenMostrar").attr("src",url)
  }

// function activeNavItem(){
//   let url = window.location.href
//   url = url.slice(-url.length+22,-1)
//   document.querySelectorAll('a').forEach(element => {
//     if(element.href.includes(url)){
//       element.classList.add('active')
//     }
//   })
// }

// activeNavItem()

