$(document).ready(function(){
    //$('body').removeClass('ui-overlay-a');
    //$('#waiter-category').removeClass('ui-page-theme-a');
    //$('#waiter-category').find('*').attr('data-role', 'none');
    //$('.ui-input-text').removeClass('ui-body-inherit');
    //$('.ui-input-text').removeClass('ui-corner-all');
    //$('.ui-input-text').removeClass('ui-shadow-inset');
    //$('.ui-input-text').removeClass('ui-input-text');
    // secure cookie: who=waiter  fid=  session=             desk
    window.categories = [];
    window.diet = [];
    window.myorder = {};
    window.desk = null;



    //init state: when in  and when out
    //if cookie desk exists, show content ,else hide
    window.desk = getCookie('desk');
    if(desk) {
        $('.form-wrapper').hide();
        $('.heading-wrapper').find('h3').text(desk);
        $('.heading-wrapper').show();

        $('.c-content').show();

    } else {
        $('.form-wrapper').show();
        $('.heading-wrapper').hide();

        $('.c-content').hide();
    }
    //get category and order and build c-content
    $.postJSON(
        '/waiter-category',
        {},
        function(response){
            //get category and diet
            window.diet = response.diet;
            window.categories = response.categories;
            buildContent(categories);
        }
    );

    //event button tapped login    set cookie desk, get myorder, show nums and show content
    $('.c-header-button').on('tap', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        //empty input
        var desk = trim($('input#desk').val());
        console.log(desk);
        if(desk == '') return;

        //set cookie and get myorder, show nums and content
        $.postJSON(
            '/waiter-category-login',
            {'desk': json(desk)},
            function(response){
                console.log('login',response);
                if(response.status == 'ok') {
                    window.myorder = response.myorder;
                    window.desk = response.desk;

                    $('.form-wrapper').slideUp();
                    $('.heading-wrapper').slideDown();
                    $('.heading-wrapper').find('h3').text(response.desk);
                    $('.c-content').slideDown();
                }

            }
        );



    });
    //event logout button tapped, clear cookie desk and hide c-content s-content
    $('.c-header-btn').on('tap', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        $.postJSON(
            '/waiter-category-logout',
            {},
            function(response){
                window.desk = null;
                window.num = null;
                $('.heading-wrapper').slideUp();
                $('.form-wrapper').slideDown();
                $('.c-content').slideUp();

            }
        );
        updater.reset();
    });

    //event category item tapped
    $(document).on('tap','.c-item',function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        var cid = $(this).data('id');
        $.postJSON(
            '/waiter-category-to-detail',
            {'cid': json(cid)},
            function(response){
                //
                if (response.next) {
                    window.location.replace(response.next);
                }

            }
        );
    });

    $('.c-footer-button-left').on('tap', function(){

        window.location.replace('/waiter-request?hh=0');
    });

    $('.c-footer-button-right').on('tap', function(){
        if(window.desk) window.location.replace('/waiter-order?hh=0');
    });
    //event search-text change

    updater.poll();

});

function buildContent(categories) {
    var p = $('.c-content').empty();
    for(var i in categories){
        var item = $('<div class="c-item">'+
                      '<h2 class="c-item-name">Heading</h2>'+
                      '<h4 class="c-item-num">Heading</h4>'+
                    '</div>');
        item.data(categories[i]);
        item.find('.c-item-name').text(categories[i].name);
        item.find('.c-item-num').text('');

        p.append(item);

    }

}



function showNum(){
    if(window.myorder){
        var left = window.myorder.left;
        var selected = window.myorder.selected;
        var doing = window.myorder.doing;
        var done = window.myorder.done;
        var confirmed = left.concat(selected).concat(doing).concat(done);
        var details = myorder.details;
        $('.c-item').each(function(){
            var cid = $(this).data('id');
            var totalnum = 0;
            for(var i in confirmed) {
                if (cid == confirmed[i].cid) totalnum += confirmed[i].num;
            }
            for(var i in details) {
                if (cid == details[i].cid) totalnum += details[i].num;
            }
            $(this).find('.c-item-num').text(totalnum);
        });
    }

}
var updater = {
    interval: 800,
    stamp: 0,
    cursor: 0,
    xhr: null,
    poll: function(){
        if(!window.desk) {
            console.log('waiting');
            setTimeout(updater.poll, updater.interval);
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