$(document).ready(function(){
    //$(this).removeClass('ui-page-theme-a');
    //$(this).find('*').attr('data-role', 'none');

    //secure cookie: who=waiter fid= session=


    //window.request
    window.customer_submits = [];
    window.customer_requests = [];
    window.cook_requests = [];

    //event logout button
    $(document).on('tap', '.logout-button', function(){
        window.location.replace('/faculty-home?hh=');
    });
    //answer cook request
    $(document).on('tap', '.cook-request-item .button', function(e){

        var item = $(this).parents('.cook-request-item');
        var fid = item.data('fid');
        $.postJSON(
            '/waiter-request',
            {'cook_request': json(fid)},
            function(response){
                console.log(response);
                if(response.status != 'ok') return;
                window.cook_requests = response.buffer;
                showCookRequests(window.cook_requests);
            }
        );
    });
    //answer customer request
    $(document).on('tap', '.customer-request-item .button', function(e){

        var item = $(this).parents('.customer-request-item');
        var desk = item.data('desk');
        $.postJSON(
            '/waiter-request',
            {'customer_request': json(desk)},
            function(response){
                console.log(response);
                if(response.status != 'ok') return;
                window.customer_requests = response.buffer;
                showCustomerRequests(window.customer_requests);
            }
        );
    });
    //answer customer submit
    $(document).on('tap', '.customer-submit-item .button', function(e){

        var item = $(this).parents('.customer-submit-item');
        var desk = item.data('desk');
        $.postJSON(
            '/waiter-request',
            {'customer_submit': json(desk)},
            function(response){
                console.log(response);
                if(response.status != 'ok') return;
                window.customer_submits = response.buffer;
                showCustomerSubmits(window.customer_submits);
            }
        );
    });
    $(document).on('tap', '.request-footer-button-left', function(){
        window.location.replace('/waiter-transfer?hh=');
    });
    $(document).on('tap', '.request-footer-button-right', function(){
        window.location.replace('/waiter-category?hh=');
    });


    //cook request updater
    cookRequestUpdater.poll();

    //customer request updater
    customerRequestUpdater.poll();

    //customer submit updater
    customerSubmitUpdater.poll();
});

function showCookRequests(requests) {
    var p = $('.cook-request').empty();
    if(!requests) return;

    for(var i in requests) {
        var item = $('<div class="request-item cook-request-item">'+
                        '<h3 class="request-item-heading">Heading</h3><a class="button request-item-button" href="javascript:void(0)">回应</a>'+
                      '</div>');
        var d = {'fid': requests[i][0], 'name': requests[i][1]};
        item.data(d);
        item.find('.request-item-heading').text(d['name']+'师傅');
        p.append(item);

    }
}
function showCustomerRequests(requests) {

    $('.customer-request-item').remove();
    if(!requests) return;

    var p = $('.customer-request ');
    for(var i in requests) {
        var item = $('<div class="request-item customer-request-item">'+
                        '<h3 class="request-item-heading">Heading</h3><a class="button request-item-button" href="javascript:void(0)">接受</a>'+
                      '</div>');
        item.data('desk', requests[i]);
        item.find('.request-item-heading').text(requests[i]+'桌');
        p.append(item);

    }
}
function showCustomerSubmits(submits){
    $('.customer-submit-item').remove();
    if(!submits) return;
    var p = $('.customer-request ');

    for(var i in submits){
        var item = $('<div class="request-item customer-submit-item">'+
                        '<h3 class="request-item-heading">Heading</h3><a class="button request-item-button" href="javascript:void(0)">下单</a>'+
                      '</div>');
        item.data('desk', submits[i]);
        item.find('.request-item-heading').text(submits[i]+'桌');
        p.prepend(item);
    }
}



var cookRequestUpdater = {
    interval: 800,
    stamp: 0,
    cursor: 0,
    poll: function(){
        console.log('polling:',cookRequestUpdater.cursor);
        cookRequestUpdater.cursor += 1;
        $.ajax({
            url: '/waiter-cook-request-update',
            type: 'POST',
            dataType: 'json',
            data: {'stamp': json(cookRequestUpdater.stamp), '_xsrf': getCookie('_xsrf')},
            success: cookRequestUpdater.onSuccess,
            error: cookRequestUpdater.onError
        });

    },

    onSuccess: function(response){
        console.log('polling response',response);

        if(response.status != 'ok') {
            window.location.replace(response.next);
            return;
        }

        window.cook_requests = response.buffer;
        cookRequestUpdater.stamp = response.stamp;
        showCookRequests(window.cook_requests);


        cookRequestUpdater.interval = 800;
        setTimeout(cookRequestUpdater.poll, cookRequestUpdater.interval);//wait updater.stamp below
    },

    onError: function(response) {
        cookRequestUpdater.interval = cookRequestUpdater.interval*2;
        setTimeout(cookRequestUpdater.poll, cookRequestUpdater.interval);
    }
};

var customerRequestUpdater = {
    interval: 800,
    stamp: 0,
    cursor: 0,
    poll: function(){
        console.log('polling:',customerRequestUpdater.cursor);
        customerRequestUpdater.cursor += 1;
        $.ajax({
            url: '/waiter-customer-request-update',
            type: 'POST',
            dataType: 'json',
            data: {'stamp': json(customerRequestUpdater.stamp), '_xsrf': getCookie('_xsrf')},
            success: customerRequestUpdater.onSuccess,
            error: customerRequestUpdater.onError
        });

    },

    onSuccess: function(response){
        console.log('polling response',response);

        if(response.status !== 'ok') {
            window.location.replace(response.next);
            return;
        }

        window.customer_requests = response.buffer;
        customerRequestUpdater.stamp = response.stamp;
        showCustomerRequests(window.customer_requests);


        customerRequestUpdater.interval = 800;
        setTimeout(customerRequestUpdater.poll, customerRequestUpdater.interval);//wait updater.stamp below
    },

    onError: function(response) {
        customerRequestUpdater.interval = customerRequestUpdater.interval*2;
        setTimeout(customerRequestUpdater.poll, customerRequestUpdater.interval);
    }
};


var customerSubmitUpdater = {
    interval: 800,
    stamp: 0,
    cursor: 0,
    poll: function(){
        console.log('polling:',customerSubmitUpdater.cursor);
        customerSubmitUpdater.cursor += 1;
        $.ajax({
            url: '/waiter-customer-submit-update',
            type: 'POST',
            dataType: 'json',
            data: {'stamp': json(customerSubmitUpdater.stamp), '_xsrf': getCookie('_xsrf')},
            success: customerSubmitUpdater.onSuccess,
            error: customerSubmitUpdater.onError
        });

    },

    onSuccess: function(response){
        console.log('polling response',response);

        if(response.status !== 'ok') {
            window.location.replace(response.next);
            return;
        }

        window.customer_submits = response.buffer;
        customerSubmitUpdater.stamp = response.stamp;
        showCustomerSubmits(window.customer_submits);


        customerSubmitUpdater.interval = 800;
        setTimeout(customerSubmitUpdater.poll, customerSubmitUpdater.interval);//wait updater.stamp below
    },

    onError: function(response) {
        customerSubmitUpdater.interval = customerSubmitUpdater.interval*2;
        setTimeout(customerSubmitUpdater.poll, customerSubmitUpdater.interval);
    }
};

