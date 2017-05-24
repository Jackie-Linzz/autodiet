$(document).ready(function(){
    //secure cookie: who fid session

    window.transfer = null;



    //event item button tapped
    $(document).on('tap', '.transfer-item-button', function(){
        //disable for 5s
        var item = $(this).parent();
        var uid = item.data('finish')[0];
        $.postJSON(
            '/waiter-transfer-answer',
            {'uid': json(uid)},
            function(response){
                window.transfer = response.transfer;
                showContent();
            }
        );
    });

    //event back button tapped
    $(document).on('tap', '.button-footer-left', function(){
        window.location.replace('/waiter-request?hh=');
    });
    //event order button tapped
    $(document).on('tap', '.button-footer-right', function(){
        window.location.replace('/waiter-category?hh=');
    });

    //poll for latest
    updater.poll();

});

function showContent(){
    var p = $('.transfer-content').empty();
    if(window.transfer) {

        var transfer = window.transfer;
        for(var i in transfer) {
            var item = $('<div class="transfer-item">'+
                              '<h3 class="transfer-item-heading">Heading</h3>'+
                              '<a class="button transfer-item-button" href="javascript:void(0)">Button Text</a>'+
                            '</div>');
            item.data('finish', transfer[i]);
            item.find('.transfer-item-heading').text(transfer[i][1]+' '+transfer[i][2]+'份:'+transfer[i][3]+'桌:'+transfer[i][5]);
            p.append(item);
        }


    }
}

var updater = {
    stamp: 0,
    interval: 800,
    cursor: 0,
    poll: function(){
        console.log(updater.cursor);
        updater.cursor += 1;
        $.ajax({
            url: '/waiter-transfer-update',
            type: 'POST',
            data:{'stamp': json(updater.stamp)},
            dataType: 'json',
            success: updater.onSuccess,
            error: updater.onError
        });
    },

    onSuccess: function(response) {
        updater.interval = 800;
        setTimeout(updater.poll, updater.interval);
        if (response.status != 'ok') return;
        updater.stamp = response.stamp;
        window.transfer = response.transfer;
        showContent();
    },

    onError: function(response) {
        updater.interval *= 2;
        setTimeout(updater.poll, updater.interval);
    }
};