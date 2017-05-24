$(document).ready(function(){
    //$('#waiter-search').removeClass('ui-page-theme-a');
    //$('#waiter-search').find('*').attr('data-role', 'none');

    //secure cookie: who= fid= session= , cookie: desk
    //cookie desk
    window.desk = getCookie('desk');
    window.diet = null;
    window.myorder = null;
    window.search = [];

    //get diet and myorder
    $.postJSON(
        '/waiter-search',
        {},
        function(response) {
            if(auth(response)) {

                window.myorder = response.myorder;
                window.diet = response.diet;
            }
            updater.poll();
        }
    );
    //event back button tapped
    $(document).on('tap', '.search-back-button', function(){
        window.location.replace('/waiter-order?hh=');
    });

    //event search-text change
    $(document).on('change', '.search-text', function(){
        var id = trim($(this).val());
        id = Number(id);
        window.search = [];
        for(var i in window.diet){
            if(window.diet[i].id == id) window.search.push(diet[i]);
        }
        showContent();
        showNum();
    });

    //event order button
    $(document).on('tap', '.d-item-button-confirm', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        var item = $(this).parents('.d-item');
        var id = item.data('id');
        var demand = item.find('.d-item-demand').val();
        var ins = makeins('+', {'id':id, 'demand':demand});

        $.postJSON(
            '/waiter-order-order',
            {'instruction': json(ins)},
            function(response){
                if(auth(response)) {
                    window.myorder = response.myorder;
                    showNum();
                }
            }
        );
    });
    //event button cancel
    $(document).on('tap', '.d-item-button-cancel', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        var id = $(this).parents('.d-item').data('id');
        var ins = makeins('-', {'id': id});
        $.postJSON(
            '/waiter-order-order',
            {'instruction': json(ins)},
            function(response){
                if(auth(response)) {
                    window.myorder = response.myorder;
                    showNum();
                }
            }

        );
    });




});

function showContent(){
    //remove existing ones
    var p = $('.s-items').empty();

    var desk = window.desk;
    if(desk == '' || !desk) return;
    var details = window.search;

    for(var i in details) {
        var item = $('<div class="d-item">'+
                          '<div class="w-clearfix d-item-row">'+
                            '<div class="d-item-name">'+
                              '<h3 class="d-item-name-heading">Heading</h3>'+
                            '</div>'+
                            '<div class="d-item-price">'+
                              '<h3 class="d-item-price-heading">Heading</h3>'+
                            '</div>'+
                            '<div class="d-item-num">'+
                              '<h3 class="d-item-num-heading">Heading</h3>'+
                            '</div>'+
                            '<div class="d-item-button"><a class="button d-item-button-confirm" href="#">点</a>'+
                            '</div>'+
                          '</div>'+
                          '<div class="w-clearfix d-item-row">'+
                            '<div class="d-item-demand">This is some text inside of a div block.</div>'+
                            '<div class="d-item-btn"><a class="button d-item-button-cancel" href="#">X</a>'+
                            '</div>'+
                          '</div>'+
                        '</div>');

        item.data(details[i]);

        item.find('.d-item-name-heading').text(details[i].name);
        item.find('.d-item-price-heading').text(details[i].price);
        item.find('.d-item-num-heading').text(details[i].num);
        item.find('.d-item-demand').text('');

        p.prepend(item);
    }

}
function getNum(id) {
    id = id -0;
    var num = 0;
    var details = window.myorder.details;
    for(var i in details) {
        if(id == details[i].id) {
            num += details[i].num;
        }
    }
    return num;
}
function showNum(){
    $('.d-item').each(function(){
        $(this).find('.d-item-num-heading').text(getNum($(this).data('id')));
    });
}

var updater = {
    interval: 800,
    stamp: 0,
    cursor: 0,
    poll: function(){
        if(!window.desk) {
            window.location.replace('/');
            return;
        }
        console.log('polling:',updater.cursor);
        updater.cursor += 1;
        $.ajax({
            url: '/waiter-order-update',
            type: 'POST',
            dataType: 'json',
            data: {'stamp': json(updater.stamp), '_xsrf': getCookie('_xsrf')},
            success: updater.onSuccess,
            error: updater.onError
        });

    },

    onSuccess: function(response){
        console.log('polling response',response);

        if(auth(response)) {
            window.myorder = response.myorder;
            updater.stamp = window.myorder.stamp;
            showContent();
        }

        updater.interval = 800;
        setTimeout(updater.poll, updater.interval);//wait updater.stamp below


    },

    onError: function(response) {
        updater.interval = updater.interval*2;
        setTimeout(updater.poll, updater.interval);
    }
};