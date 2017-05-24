$(document).ready(function(){
    //remove jqm css
    //$('#customer-overlay').removeClass('ui-page-theme-a');
    //$('#customer-overlay').find('*').attr('data-role', 'none');

    //secure cookie: who=customer, fid=, session=     cookie: desk= cid=  item_id=

    window.diet = null;
    window.myorder = null;
    window.cid = null;
    window.item_id = null;

    //retrieve data from sever
    $.postJSON(
        '/customer-overlay',
        {},
        function(response) {
            if(response.status != 'ok') {
                window.location.replace(response.next);
                return;
            }

            window.diet = response.diet;
            window.myorder = response.myorder;
            window.cid = response.cid;
            window.item_id = response.item_id;
            showContent();
        }
    );

    //event confirm button tapped
    $(document).on('tap', '.overlay-confirm', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        //send instruction and get latest myorder
        var demand = trim($('.overlay-demand').val());
        var ins = makeins('+', {'id': item_id, 'demand': demand});
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


    //event cancel button tapped
    $(document).on('tap', '.overlay-cancel', function(){
        window.location.replace('/customer-detail?hh=0');

    });

    //polling for latese myorder
    updater.poll();


});



function showContent() {
    if(!item_id) return;
    if(!diet) return;

    for(var i in diet) {
        if(diet[i].id == item_id) {
            var item = diet[i];
            $('.overlay-heading').text(item.name);
            $('.overlay-image').attr('src', '/static/pictures/'+item.picture);
            $('.overlay-price').text(item.price);
            $('.overlay-num').text('');
            $('.overlay-desc').text(item.description);
        }
    }
    showNum();
}

function showNum() {
    if(!window.myorder) return;
    var left = window.myorder.left;
    var selected = window.myorder.selected;
    var doing = window.myorder.doing;
    var done = window.myorder.done;
    var confirmed = left.concat(selected).concat(doing).concat(done);

    var details = window.myorder.details;

    var total = 0;
    for(var i in confirmed) {
        if(confirmed[i].id == item_id) total += confirmed[i].num;
    }
    for(var i in details) {
        if(details[i].id == item_id) total += details[i].num;
    }
    $('.overlay-num').text(total);


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

        if(response.status !== 'ok') {
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