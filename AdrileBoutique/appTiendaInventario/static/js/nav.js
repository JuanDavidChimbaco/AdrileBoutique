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
    $(this).siblings().find("ul").find("li").removeClass("active"); // remueve la clase active de los sub menus
})
$(".menu-btn").click(function () {
    $(".sidebar").toggleClass("active");
})