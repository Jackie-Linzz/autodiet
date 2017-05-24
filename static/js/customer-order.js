$(document).ready(function(){
    //remove jqm css
    //$('#customer-order').removeClass('ui-page-theme-a');
    //$('#customer-order').find('*').attr('data-role', 'none');

    // secure cookie: who=customer session=str  cookie:   desk=str

    window.myorder = null;

    //retrieve myorder from /customer-order
    $.postJSON(
        '/customer-order',
        {},
        function(response) {
            console.log(response);
            if(response.status != 'ok') {
                window.location.replace(response.next);
                return;
            }

            window.myorder = response.myorder;

            showCurrentOrder();

        }
    );

    //event show-history button tapped
    $(document).on('tap', '.show-history-button', function(){
        window.location.replace('/customer-history?hh=');
    });
    //event cancel button tapped
    $(document).on('tap', '.order-item-button-x', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        var item = $(this).parents('.order-item');
        var uid = item.data('uid');
        var ins = makeins('-', {'uid': uid});
        $.postJSON(
            '/customer-make-order',
            {'instruction': json(ins)},
            function(response) {
                if(response.status != 'ok') return;
                window.myorder = response.myorder;
                showCurrentOrder();

            }
        );
    });
    //event gdmand changed
    $(document).on('change', '.order-gdemand', function(){
        var gdemand = trim($('.order-gdemand').val());
        var ins = makeins('gd', gdemand);
        $.postJSON(
            '/customer-make-order',
            {'instruction': json(ins)},
            function(response) {
                if(response.status != 'ok') return;
                window.myorder = response.myorder;
                showCurrentOrder();

            }
        );
    });

    //event submit button tapped
    $(document).on('tap', '.footer-button-right', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        function submit(){
            if(!myorder) return;
            if(!myorder.stamp) return;
            var ins = makeins('submit', window.myorder.stamp);
            console.log(ins);
            $.postJSON(
                '/customer-make-order',
                {'instruction': json(ins)},
                function(response) {
                    if(response.status != 'ok') return;
                    window.myorder = response.myorder;
                    if(!myorder) return;

                    showCurrentOrder();
                }
            );
        }

        setTimeout(submit, 800);

    });

    //event back button tapped
    $(document).on('tap', '.footer-button-left', function(){
        window.location.replace('/customer-category?hh=0');
    });

    //poll
    updater.poll();

});

function showCurrentOrder() {
    // clear
    var last = $('.order-item-last');
    last.find('.order-item-price-heading').text(0);
    last.siblings().remove();

    if(!window.myorder) return;

    var content = $('.order-content');
    var details = window.myorder.details;
    var left = window.myorder.left;
    var selected = window.myorder.selected;
    var doing = window.myorder.doing;
    var done = window.myorder.done;

    var confirmed = done.concat(doing).concat(selected).concat(left);

    var total_price = 0;
    for(var i in confirmed) {
        var item = new_item(confirmed[i]);
        item.find('.order-item-button-x').remove();
        last.before(item);
        total_price += confirmed[i].price * confirmed[i].num;
    }
    for(var i in details) {
        var item = new_item(details[i]);
        last.before(item);
        total_price += details[i].price * details[i].num;
    }

    last.find('.order-item-price-heading').text(total_price);
    var gdemand = window.myorder.gdemand;
    $('.order-gdemand').val(gdemand);

    showButtonStatus();

}

function showButtonStatus(){
    if(!window.myorder) return;
    var status = window.myorder.status;
    var button = $('.footer-button-right');
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

function new_item(item) {
    var item$ = $('<div class="order-item">'+
                  '<div class="w-clearfix order-item-row">'+
                   '<div class="order-item-name">'+
                      '<h4 class="order-item-name-heading">Heading</h4>'+
                    '</div>'+
                    '<div class="order-item-num">'+
                      '<h4 class="order-item-num-heading">Heading</h4>'+
                    '</div>'+
                    '<div class="order-item-price">'+
                      '<h4 class="order-item-price-heading">Heading</h4>'+
                    '</div>'+
                  '</div>'+
                  '<div class="w-clearfix order-item-row">'+
                    '<div class="order-item-demand">This is some text inside of a div block.</div>'+
                    '<div class="order-item-x"><a class="button order-item-button-x" href="javascript:void(0)">X</a>'+
                    '</div>'+
                  '</div>'+
                '</div>');
    item$.data(item);
    item$.find('.order-item-name-heading').text(item.name);
    item$.find('.order-item-num-heading').text(item.num);
    item$.find('.order-item-price-heading').text(item.price);
    item$.find('.order-item-demand').text(item.demand);
    return item$;

}

var updater = {
    interval: 800,
    stamp: 0,
    cursor: 0,
    poll: function(){

        console.log('polling:',updater.cursor);
        updater.cursor += 1;
        $.ajax({
            url: '/customer-order-update',
            type: 'POST',
            dataType: 'json',
            data: {'stamp': json(updater.stamp), '_xsrf': getCookie('_xsrf')},
            success: updater.onSuccess,
            error: updater.onError
        });

    },

    onSuccess: function(response){
        console.log('polling response',response);

        //wait updater.stamp below
        if(response.status != 'ok') {
            window.location.replace(response.next);
            return;
        }

        window.myorder = response.myorder;
        updater.stamp = window.myorder.stamp;
        showCurrentOrder();


        updater.interval = 800;
        setTimeout(updater.poll, updater.interval);

    },

    onError: function(response) {
        updater.interval = updater.interval*2;
        setTimeout(updater.poll, updater.interval);
    }
};