$(document).ready(function(){

    //get company-info
    $('#company-refresh').on('tap', function(){
        $.ajax({
            url: '/company-data',
            type: 'POST',
            data: {},
            dataType: 'json',
            success: function(response) {
                console.log(response);
                if(response.status != 'ok') {
                    window.location.replace(response.next);
                    return;
                }
                  $('.company-name').val(response.name);
                  $('.company-shortname').val(response.shortname);
                  $('.company-location').val(response.location);
                  $('.company-desc').val(response.desc);
                  $('.company-welcome').val(response.welcome);
            },
            error: function(response){
                console.log(response);
                console.log('get company info error');
            }
        });
    });
    $('#company-refresh').trigger('tap');


    //company-info submit
    $('#company-button').on('tap', function(){
        var name = trim($('.company-name').val());
        var shortname = trim($('.company-shortname').val());
        var location = trim($('.company-location').val());
        var desc = trim($('.company-desc').val());
        var welcome = trim($('.company-welcome').val());

        $.postJSON(
            '/company-info',
            {'name': json(name), 'shortname':json(shortname), 'location': json(location), 'desc': json(desc), 'welcome': json(welcome)},
            function(response){
                if(response.status != 'ok') return;
                $('.company-name').val(response.name);
                $('.company-shortname').val(response.shortname);
                $('.company-location').val(response.location);
                $('.company-desc').val(response.desc);
                $('.company-welcome').val(response.welcome);
            }
        );
    });
});