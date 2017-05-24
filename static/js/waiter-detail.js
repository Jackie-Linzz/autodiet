$(document).ready(function(){
    //$('#waiter-detail').removeClass('ui-page-theme-a');
    //$('#waiter-detail').find('*').attr('data-role', 'none');
    // cookie: who=waiter fid= session=  secure;      desk=  cid= not secure
    window.diet = null;
    window.categories = null;
    window.desk = null;
    window.myorder = null;
    window.cid = null;

    //get diet and myorder
    $.postJSON(
        '/waiter-detail',
        {},
        function(response){
            console.log(response);
            window.diet = response.diet;
            window.myorder = response.myorder;
            window.categories = response.categories;
            window.desk = response.desk;
            window.cid = response.cid;
            //d-header-heading
            for(var i in categories){
                if(categories[i].id == window.cid) {
                    $('.d-header-heading').text(categories[i].name);
                    break;
                }
            }
            buildContent();

            //poll
            updater.poll();
        }
    );

    //event button add tapped
    $(document).on('tap', '.d-item-button-confirm', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        //send ins
        var item = $(this).parents('.d-item');
        var id = item.data('id');
        var demand = trim(item.find('.d-item-demand').val());
        var ins = makeins('+', {'id':id, 'demand':demand});
        item.find('.d-item-demand').val('');
        $.postJSON(
            '/waiter-detail-order',
            {'instruction': json(ins)},
            function(response){
                window.myorder = response.myorder;
                showNum();
            }

        );
    });

    //event button delete tapped
    $(document).on('tap', '.d-item-button-cancel', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        //send ins
        var id = $(this).parents('.d-item').data('id');
        var ins = makeins('-', {'id': id});
        $.postJSON(
            '/waiter-detail-order',
            {'instruction': json(ins)},
            function(response){

                window.myorder = response.myorder;
                showNum();

            }

        );

    });

    $(document).on('tap', '.d-footer-button-left', function(){
        window.location.replace('/waiter-category?hh=');
    });
    $(document).on('tap', '.d-footer-button-right', function(){
        window.location.replace('/waiter-order?hh=');
    });


});

function buildContent(){
    var p = $('.d-content').empty();
    console.log('window.cid',window.cid);
    console.log('window.diet', window.diet);
    if(window.cid && window.diet){

        var cid = window.cid;
        var diet = window.diet;
        for (var i in diet) {
            if(cid == diet[i].cid) {

                var item = detailItem(diet[i]);

                p.append(item);
            }
        }
    }

}

function detailItem(diet){
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
                      '<div class="d-item-demand">This is some text inside of a div&nbsp;</div>'+
                      '<div class="d-item-btn"><a class="button d-item-button-cancel" href="javascript:void(0)">X</a>'+
                      '</div>'+
                    '</div>'+
                  '</div>');

                item.data(diet);
                item.find('.d-item-name-heading').text(diet.name);
                item.find('.d-item-price-heading').text(diet.price);
                item.find('.d-item-num-heading').text('');
                item.find('.d-item-demand').val('');
    return item;
}

function getNum(id) {

    var num = 0;
    var details = window.myorder.details;
    var left = window.myorder.left;
    var selected = window.myorder.selected;
    var doing = window.myorder.doing;
    var done = window.myorder.done;
    var all = details.concat(left).concat(selected).concat(doing).concat(done);
    for(var i in all) {
        if(id == all[i].id) {
            num += all[i].num;
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
    xhr: null,
    poll: function(){
        if(!window.desk) {
            console.log('no desk');

            return;
        }
        console.log('polling:',updater.cursor);
        updater.cursor += 1;
        updater.xhr = $.ajax({
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

        //wait updater.stamp below
        if(response.status != 'ok') {
            window.location.replace(response.next);
            return;
        }

        window.myorder = response.myorder;
        updater.stamp = window.myorder.stamp;
        showNum();
        updater.interval = 800;
        setTimeout(updater.poll, updater.interval);


    },

    onError: function(response, error) {
        console.log(error);
        updater.interval = updater.interval*2;
        setTimeout(updater.poll, updater.interval);
    },

    reset: function(){
        updater.stamp = 0;
        updater.cursor = 0;
        updater.interval = 800;
        updater.xhr.abort();
    }
};