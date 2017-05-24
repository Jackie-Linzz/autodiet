$(document).ready(function(){
    //secure cookie: who= fid= session=

    //button work tapped
    $('#work').on('tap', function(){
        $.postJSON(
            '/faculty-home',
            {'screenWidth': json(window.screen.width)},
            function(response){
                window.location.replace(response.next);
            }
        );
    });
    //button setting tapped
    $('#setting').on('tap', function(){
        window.location.replace('/faculty-secret');
    });
    //button logout tapped
    $('#logout').on('tap', function(){
        $.postJSON(
            '/faculty-logout',
            {},
            function(response){
                window.location.replace(response.next);
            }
        );
    });
});