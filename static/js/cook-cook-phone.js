$(document).ready(function() {
    // secure cookie: who fid session

    //init
    window.mycook = null;
    window.byway_selected = [];

    //retrieve mycook
    //retrieve mycook
    $.postJSON(
        '/cook-cook',
        {},
        function (response) {
            if (auth(response)) {
                window.mycook = response.mycook;
                showContent();
            }

        }
    );

    //event button-other
    $(document).on('tap', '.button-other', function () {
        window.location.replace('/cook-cook-other-phone?hh=');
    });
    //event button byway select
    $(document).on('tap', '.byway-item-button', function (e) {
        //disable for 1s
        if (!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 1000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        var item = $(this).parents('.byway-item');
        var flag = !item.data('flag');
        item.data('flag', flag);
        if (flag) {
            item.addClass('byway-item-selected');
            $(this).addClass('byway-item-button-selected');

        } else {
            item.removeClass('byway-item-selected');
            $(this).removeClass('byway-item-button-selected');
        }

    });
    //event button accept
    $('.button-accept').on('tap', function (e) {
        //disable for 1s
        if (!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 1000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect


        window.byway_selected = [];
        if (mycook.current) window.byway_selected.push(mycook.current.uid);
        $('.byway-item').each(function () {
            if ($(this).data('flag')) window.byway_selected.push($(this).data('uid'));
        });
        var ins = {'accept': window.byway_selected};
        $.postJSON(
            '/cook-instruction',
            {'instruction': json(ins)},
            function (response) {
                if (auth(response)) {
                    window.mycook = response.mycook;
                    showContent();
                }
            }
        );
    });
});

function showContent(){
    if (!window.mycook) return;
    var current = window.mycook.current;
    //show current item

    if(current){
        $('.current-item-name').text(current['name']);
        $('.current-item-num').text(current['desk']+' : '+current['num']);
        $('.current-item-demand').text(current['demand']);
    } else {
        $('.current-item-name').text('无');
        $('.current-item-num').text('..');
        $('.current-item-demand').text('..');
    }

    //show byway
    $('.byway-item').remove();
    var byway = window.mycook.byway;
    var p = $('.div-byway');

    for(var i in byway) {
        var item = buildBywayItem(byway[i]);
        p.append(item);
    }

}

function buildBywayItem(order){
    var item = $('<div class="byway-item">'+
        '<h3 class="byway-item-name">Heading</h3>'+
        '<h6 class="byway-item-num">Heading</h6>'+
        '<div class="byway-item-demand">This is some text inside of a div block.</div><a class="button byway-item-button" href="javascript:void(0)">Button Text</a>'+
      '</div>');
    item.data(order);
    item.find('.byway-item-name').text(order['name']);
    item.find('.byway-item-num').text(order['desk']+'桌:'+order['num']+'份');
    item.find('.byway-item-demand').text(order['demand']);
    return item;
}
