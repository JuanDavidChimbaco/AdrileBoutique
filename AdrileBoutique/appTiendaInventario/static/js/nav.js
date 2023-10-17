$(document).ready(function() {
    // Obtener la URL actual
    var currentUrl = window.location.pathname;

    // Recorrer todos los elementos de menú y agregar la clase "active" según la URL actual
    $(".menu-nav ul li").each(function() {
        var link = $(this).find("a").attr("href");
        if (currentUrl === link) {
            $(this).addClass("active");
        }
    });
});



$(".menu-nav > ul > li").click(function(e){
    $(this).siblings().removeClass("active");//remueve la clase activa
    $(this).toggleClass("active"); //Agrega la clase activa al selecionado
    $(this).find("ul").slideToggle(); // abre el sub menu
    $(this).siblings().find("ul").slideUp(); // cierra otros sub menus si hay otro abierto
    $(this).siblings().find("ul").find("li").removeClass("active"); // remueve la clase active de los otros sub menus
})

// Función para activar el sidebar en pantallas más grandes que la versión móvil
function activateSidebar() {
    if (window.innerWidth < 768) { // Cambia el 768 al ancho que consideres como no móvil
      $(".sidebar").addClass("active");
    } else {
      $(".sidebar").removeClass("active");
    }
  }
  
  // Llama a la función al cargar la página
  activateSidebar();
  
  // Llama a la función cuando se redimensiona la ventana
  $(window).on("resize", activateSidebar);


// Función para activar o desactivar el menú en dispositivos móviles
$(".menu-btn").click(function() {
  $(".my-container").toggleClass("hide");
});
