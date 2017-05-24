$(document).ready(function(){
    //remove jqm css
    //$('#customer-detail').removeClass('ui-page-theme-a');
    //$('#customer-detail').find('*').attr('data-role', 'none');

    //cookie: who=customer, desk=, session=, cid=

    //init
    //alert('page init');
    window.diet = null;
    window.myorder = null;
    window.categories = null;
    window.cid = null;


    //retrieve data from '/customer-detail'
    $.postJSON(
        '/customer-detail',
        {},
        function(response) {
            if(response.status != 'ok') {
                window.location.replace(response.next);
                return;
            }

            window.diet = response.diet;
            window.myorder = response.myorder;
            window.cid = response.cid;
            window.categories = response.categories;
            buildContent();
            showNum();
        }
    );

    // event item-image tapped
    $(document).on('tap', '.detail-item-image', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        //send item-id and transfer to overlay
        var item = $(this).parent();
        $.postJSON(
            '/customer-detail-transfer',
            {'item_id': json(item.data('id'))},
            function(response) {
                if(response.status != 'ok') return;
                window.location.replace(response.next);
            }
        );
    });

    // event item-button tapped
    $(document).on('tap', '.detail-item-button', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        //send instruction to server
        var item = $(this).parent();
        var ins = makeins('+', {'id': item.data('id')});
        $.postJSON(
            '/customer-make-order',
            {'instruction': json(ins)},
            function(response) {
                if(response.status != 'ok') return;
                window.myorder = response.myorder;
                showNum();
            }
        );
    });

    // event footer-button-right tapped    ################need to change
    $('.footer-button-right').on('tap', function(){
        console.log('footer-button-right tapped');
        window.location.replace('/customer-order?hh=0');
    });

    // event footer-button-left tapped
    $('.footer-button-left').on('tap', function(){
        console.log('footer-button-left tapped');
        window.location.replace('/customer-category?hh=0');
    });


    // polling for latest myorder
    updater.poll();
});



function buildContent(){
    //set category heading
    for(var j in categories){
        if(categories[j].id == window.cid) {
            $('.d-header-heading').text(categories[j].name);
            break;
        }
    }

    //
    var pl = $('.detail-left').empty();
    var pr = $('.detail-right').empty();
    for(var i in diet) {
        if(diet[i].cid == window.cid) {
            var item = buildItem(diet[i]);

            if(pl.height() > pr.height()) {
                pr.append(item);
            } else {
                pl.append(item);
            }

        }
    }
}
function buildItem(diet) {
    var item = $('<div class="detail-item">'+
                    '<img class="detail-item-image" src="" alt="no image">'+
                    '<h2 class="detail-item-heading">Heading</h2>'+
                    '<h5 class="detail-item-price">Heading</h5>'+
                    '<h6 class="detail-item-num">Heading</h6><a class="button detail-item-button" href="javascript:void(0)">点</a>'+
                  '</div>');
            //console.log(diet[i]);
            item.data(diet);
            item.find('.detail-item-image').attr('src', '/static/pictures/'+diet.picture);
            if(diet.picture == '') item.find('.detail-item-image').attr('src', 'javascript:void(0)');
            item.find('.detail-item-heading').text(diet.name);
            item.find('.detail-item-price').text(diet.price);
            item.find('.detail-item-num').text('');
    return item;
}

function showNum() {
    if(!window.myorder) return;
    var left = window.myorder.left;
    var selected = window.myorder.selected;
    var doing = window.myorder.doing;
    var done = window.myorder.done;
    var confirmed = left.concat(selected).concat(doing).concat(done);
    var details = window.myorder.details;


    $('.detail-item').each(function(){
        var total = 0;
        for(var i in confirmed) {
            if(confirmed[i].id == $(this).data('id')) total += confirmed[i].num;
        }
        for(var i in details) {
            if(details[i].id == $(this).data('id')) total += details[i].num;
        }
        $(this).find('.detail-item-num').text(total);
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