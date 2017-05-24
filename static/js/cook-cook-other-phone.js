$(document).ready(function(){
    // secure cookie: who fid session

    //init
    window.mycook = null;
    window.byway_selected = [];

    //retrieve mycook
    $.postJSON(
        '/cook-cook',
        {},
        function(response) {
            if(auth(response)) {
                window.mycook = response.mycook;
                showContent();
            }
        }
    );
    //event button-other
    $(document).on('tap', '.button-other', function(){
        window.location.replace('/cook-cook-phone?hh=');
    });
    //event button refuse
    $('.current-button-refuse').on('tap', function(e){
        //disable for 1s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 1000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        var ins = {'refuse': null};
        $.postJSON(
            '/cook-instruction',
            {'instruction': json(ins)},
            function(response){
                if(auth(response)) {
                    window.mycook = response.mycook;
                    showContent();
                }
            }
        );
    });
    //event button finish
    $(document).on('tap', '.doing-item-button', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        var uid = $(this).parents('.doing-item').data('uid');
        var ins = {'finish': uid};
        $.postJSON(
            '/cook-instruction',
            {'instruction': json(ins)},
            function(response){
                if(auth(response)) {
                    window.mycook = response.mycook;
                    showContent();
                }
            }
        );
    });
    //event button cancel
    $(document).on('tap', '.doing-item-button-cancel', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        var uid = $(this).parents('.doing-item').data('uid');
        var ins = {'cancel': uid};
        $.postJSON(
            '/cook-instruction',
            {'instruction': json(ins)},
            function(response){
                if(auth(response)) {
                    window.mycook = response.mycook;
                    showContent();
                }
            }
        );
    });
});

function showContent(){
    if (!window.mycook) return;



    //show doing
    var doing = window.mycook.doing;
    $('.doing-item').remove();
    var p = $('.div-doing').empty();
    for(var i in doing){
        var item = buildDoingItem(doing[i]);
        p.append(item);
    }
}

function buildDoingItem(order){
    var item = $('<div class="doing-item">'+
        '<h3 class="doing-item-name">Heading</h3>'+
        '<h6 class="doing-item-num">Heading</h6>'+
        '<div class="doing-item-demand">This is some text inside of a div block.</div><a class="button doing-item-button" href="javascript:void(0)">Button Text</a><a class="button doing-item-button-cancel" href="#">Button Text</a>'+
      '</div>');
    item.data(order);
    item.find('.doing-item-name').text(order.name);
    item.find('.doing-item-num').text(order.desk+'桌:'+order.num+'份');
    item.find('.doing-item-demand').text(order.demand);
    return item;
}