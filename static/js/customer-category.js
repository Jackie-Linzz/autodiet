$(document).ready(function(){

    //remove jqm css
    //$('#customer-category').removeClass('ui-page-theme-a');
    //$('#customer-category').find('*').attr('data-role', 'none');

    // cookie: who=customer desk=str session=str
    // when customer select a category, it should be set as cookie cid


    window.categories = null;

    window.myorder = null;

    // retrieve categories and myorder
    $.postJSON(
        '/customer-category',
        {},
        function(response) {
            if(response.status != 'ok') {
                window.location.replace(response.next);
                return;
            }
            window.categories = response.categories;
            window.myorder = response.myorder;
            buildContent();
        }
    );

    //event button logout
    $(document).on('tap', '.button-logout', function(){
        $.postJSON(
            '/customer-category-logout',
            {'logout': 'hehe'},
            function(response) {
                console.log('goodbye');
                window.location.replace(response.next);
            }
        );
    });

    // event c-item tapped  transfer to customer-detail
    $(document).on('tap', '.c-item', function(e){
        //disable for 5s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 5000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        //send category id to set cookie cid
        $.postJSON(
            '/customer-category-transfer',
            {'category': json($(this).data('id'))},
            function(response){
                if(response.status != 'ok') return;
                window.location.replace(response.next);
            }
        );
    });

    // event customer call service
    $(document).on('tap', 'a.footer-button-left', function(e){
        //disable for 10s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 10000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);

        // send desk , actually in cookie
        $.postJSON(
            '/customer-category-request',
            {},
            function(response){
                if(response.status !== 'ok') {
                    window.location.replace(response.next);
                    return;
                }
                // request success
                $(this).text('请稍等');
                setTimeout(function(){
                    $(this).text('呼叫');
                }, 10000);

            }
        );
    });
    // transfer to /customer-order
    $(document).on('tap', 'a.foot-button-right', function(){
        window.location.replace('/customer-order?hh=0');
    });
    // polling for latest myorder
    updater.poll();
});




// according to categories
function buildContent(){
    if(window.categories == null ) return;
    var p = $('.c-content').empty();
    for(var i in categories) {
            var item$ = $('<div class="c-item"><h3 class="c-item-heading"></h3><h6 class="c-item-num"></h6></div>');
            item$.data(categories[i]);
            item$.find('.c-item-heading').text(categories[i].name);
            p.append(item$);
        }

}

function showNum(){
    if(!window.myorder) return;
    var details = window.myorder.details;

    var left = window.myorder.left;
    var selected = window.myorder.selected;
    var doing = window.myorder.doing;
    var done = window.myorder.done;
    var confirmed = left.concat(selected).concat(doing).concat(done);
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

        if(response.status != 'ok') {
            window.location.replace(response.next);
            return;
        }

        window.myorder = response.myorder;
        updater.stamp = window.myorder.stamp;
        showNum();

        updater.interval = 800;
        setTimeout(updater.poll, updater.interval);//wait updater.stamp below


    },

    onError: function(response) {
        updater.interval = updater.interval*2;
        setTimeout(updater.poll, updater.interval);
    }
};