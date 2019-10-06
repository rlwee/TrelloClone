$(document).ready(function(){
    
    console.log('doc ready');

    $.ajax({
        url: '/boards/',
        method: 'GET'
    }).done(function(response){
        $('.boards').html(response);
    });


    $.ajax({
        url: '/board/create/',
        method: 'GET'
    }).done(function(response){
        $('.boards').append(response);
    });
    

    // loadAjaxContent('/boards/', $('.boards'));
    // loadAjaxContent('/board/create', $('.boards'));
 
    // function loadAjaxContent(url, container) {
    //     $.ajax({
    //         url: url,
    //         method: 'GET'
    //     }).done(function(x){
    //         $(container).append(x);
    //     });
    // }
});