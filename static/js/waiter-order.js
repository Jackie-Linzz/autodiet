$(document).ready(function(){
    //$('#waiter-order').removeClass('ui-page-theme-a');
    //$('#waiter-order').find('*').attr('data-role', 'none');

    //secure cookie: who= fid= session= , cookie: desk
    //cookie desk
    window.desk = getCookie('desk');
    window.myorder = null;

    //get myorder
    $.postJSON(
        '/waiter-order',
        {},
        function(response) {
            if(auth(response)){
                window.desk = response.desk;
                window.myorder = response.myorder;
                showContent();
            }
        }
    );

    //event button order
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
                    showContent();
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

        var uid = $(this).parents('.d-item').data('uid');
        var ins = makeins('-', {'uid': uid});
        $.postJSON(
            '/waiter-order-order',
            {'instruction': json(ins)},
            function(response){
                if(auth(response)) {
                    window.myorder = response.myorder;
                    showContent();
                }
            }
        );
    });
    //event gdemand
    $(document).on('change', '.gdemand', function(){
        console.log('gdemand change');
        var gdemand = $(this).val();
        var ins = makeins('gd', gdemand);
        $.postJSON(
            '/waiter-order-order',
            {'instruction': json(ins)},
            function(response){

                if(auth(response)) {
                    window.myorder = response.myorder;
                    showContent();
                }

            }

        );

    });
    //event button confirm
    $(document).on('tap', '.o-footer-button-right', function(e){
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 5000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        setTimeout(submit, 800);
        var ins = {'submit': window.myorder.stamp};
        function submit() {
            $.postJSON(
                '/waiter-order-order',
                {'instruction': json(ins)},
                function(response) {
                    if(auth(response)) {
                        window.myorder = response.myorder;
                        showContent();
                    }
                }
            );
        }

    });

    //event button back
    $(document).on('tap', '.o-footer-button-left', function(){
        window.location.replace('/waiter-category?hh=');
    });
    //event button search
    $(document).on('tap', '.button-search', function(){
        window.location.replace('/waiter-search?hh=');
    });
    //event button history
    $(document).on('tap', '.button-history', function(){
        window.location.replace('/waiter-history?hh=');
    });

    //poll
    updater.poll();
});

function orderItem(order) {
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
                            '<div class="d-item-button"><a class="button d-item-button-confirm" href="javascript:void(0)">点</a>'+
                            '</div>'+
                          '</div>'+
                          '<div class="w-clearfix d-item-row">'+
                            '<div class="d-item-demand">This is some text inside of a div block.</div>'+
                            '<div class="d-item-btn"><a class="button d-item-button-cancel" href="javascript:void(0)">X</a>'+
                            '</div>'+
                          '</div>'+
                        '</div>');

        item.data(order);
        item.find('.d-item-name-heading').text(order.name);
        item.find('.d-item-price-heading').text(order.price);
        item.find('.d-item-num-heading').text(order.num);
        item.find('.d-item-demand').text(order.demand);
    return item;
}

function showContent(){
    //remove existing ones
    $('.d-item-total').siblings().remove();
    $('.order-total-heading').text(0);
    $('.gdemand').val('');

    var desk = getCookie('desk');
    if(desk == '' || !desk) return;
    var details = window.myorder.details;
    var left = window.myorder.left;
    var selected = window.myorder.selected;
    var doing = window.myorder.doing;
    var done = window.myorder.done;
    var a = left.concat(details);
    var b = done.concat(doing).concat(selected);
    var totalprice = 0;
    for(var i in b) {
        var item = orderItem(b[i]);

        item.find('.d-item-button-cancel').remove();
        totalprice += b[i].price * b[i].num;

        $('.d-item-total').before(item);
    }
    for(var i in a) {

        var item = orderItem(a[i]);
        totalprice += a[i].price * a[i].num;

        $('.d-item-total').before(item);
    }
    //total heading
    $('.order-total-heading').text(totalprice);
    //gdemand
    $('.gdemand').val(window.myorder.gdemand);

    showButtonStatus();
}

function showButtonStatus(){
    if(!window.myorder) return;
    var status = window.myorder.status;
    var button = $('.o-footer-button-right');
    if(status == 'none') {
        button.text('下单');
    } else if(status == 'ready') {
        button.text('请再次确认');
    } else if(status == 'submit' || status == 'lock') {
        button.text('正在下单...');
    } else if(status == 'confirmed') {
        button.text('已下单');
    } else {
        button.text('下单');
    }
}

var updater = {
    interval: 800,
    stamp: 0,
    cursor: 0,
    poll: function(){
        if(!window.desk) {
            console.log('no desk');
            setTimeout(updater.poll, updater.interval);
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

        if(response.status != 'ok') {
            window.location.replace(response.next);
            return;
        }

        window.myorder = response.myorder;
        updater.stamp = window.myorder.stamp;
        showContent();

        updater.interval = 800;
        setTimeout(updater.poll, updater.interval);//wait updater.stamp below

    },

    onError: function(response) {
        updater.interval = updater.interval*2;
        setTimeout(updater.poll, updater.interval);
    }
};