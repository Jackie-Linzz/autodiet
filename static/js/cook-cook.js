$(document).on('pageinit', '#cook-cook', function(){
    $('#cook-cook').removeClass('ui-page-theme-a');
    $('#cook-cook').find('*').attr('data-role', 'none');
    //cookie  who=cook
    //cookie  if id exists,use id, else use uid for anonymous working

    window.mycook = {};
    window.selected = [];

    //retrieve mycook
    $.postJSON(
        '/cook-cook',
        {},
        function(response) {
            window.mycook = response.mycook;
            showContent();
        }
    );

    //event accept button, accept current and selected byway items
    $('#cook-cook').on('tap', '.current-button-accept', function(){
        window.selected = [];
        window.selected.push($('.current-item').data('uid'));
        $('.byway-item').each(function(){
            if($(this).data('selected')) {
                window.selected.push($(this).data('uid'));
            }
        });
        //send instruction   {'accept': selected}
        var ins = makeins('accept', window.selected);
        $.postJSON(
            '/cook-cook-instruction',
            {'instruction': json(ins)},
            function(response) {
                window.mycook = response.mycook;
                showContent();
            }
        );

    });

    //event refuse button
    $('#cook-cook').on('tap', '.current-button-refuse', function(){
        var ins = makeins('refuse', '');
        $.postJSON(
            '/cook-cook-instruction',
            {'instruction': json(ins)},
            function(response) {
                window.mycook = response.mycook;
                showContent();
            }
        );
    });
    //event call button
    $('#cook-cook').on('tap', '.current-button-call', function(){
        $.postJSON(
            '/cook-call',
            {},
            function(response) {


            }
        );
    });
    //event doing-item
    //event doing-item-button
    $('#cook-cook').on('tap', '.doing-item-button', function(){
        var item = $(this).parent();
        var uid = item.data('uid');
        var ins = makeins('finish', uid);
        $.postJSON(
            '/cook-cook-instruction',
            {'instruction': json(ins)},
            function(response) {
                window.mycook = response.mycook;
                showContent();

            }
        );
    });

    //event doing-item-button-cancel
    $('#cook-cook').on('tap', '.doing-item-button', function(){
        var item = $(this).parent();
        var uid = item.data('uid');
        var ins = makeins('cancel', uid);
        $.postJSON(
            '/cook-cook-instruction',
            {'instruction': json(ins)},
            function(response) {
                window.mycook = response.mycook;
                showContent();

            }
        );
    });

    //event byway-item-button
    $('#cook-cook').on('tap', '.byway-item-button', function(){
        var item = $(this).parent();
        var selected = item.data('selected');
        selected = !selected;
        if(selected) {
            item.addClass('selected');
        } else {
            item.removeClass('selected');
        }
    });

    //poll


});

//{'uid': self.uid, 'id': self.id, 'name': self.name, 'num': self.num, 'base': self.base,
// 'price': self.price, 'order': self.order, 'demand': self.demand, 'status': self.status, 'desk': self.desk}


function showContent(){

    //show byways
    if(mycook.current) {
        //consider accept fails when the accept from this cook is byway of other cook

        //normal
        var cur = mycook.current;
        $('.current-item').data(cur);
        $('.current-item-name').text(cur.name);
        $('.current-item-num').text(cur.desk+': '+cur.num);
        $('.current-item-demand').text(cur.demand);
    }

    //show current
    if(mycook.byway) {
        $('.right-content').empty();
        var byway = mycook.byway;
        for(var i in byway) {
            var item = $('<div class="byway-item">'+
                            '<h3 class="byway-item-name"></h3>'+
                            '<h6 class="byway-item-num"></h6>'+
                            '<div class="byway-item-demand"></div>'+
                            '<a class="button byway-item-button" href="#">选择</a>'+
                        '</div>');
            item.data(byway[i]);
            item.find('.byway-item-name').text(byway[i].name);
            item.find('.byway-item-num').text(byway[i].desk+': '+byway[i].num);
            item.find('.byway-item-demand').text(byway[i].demand);
            $('.right-content').append(item);
        }
    }
    //show doings
    if(mycook.doing) {
        $('.left-content').empty();
        var doing = mycook.doing;
        for(var i in doing) {
            var item = $('<div class="doing-item">'+
                            '<h3 class="doing-item-name">Heading</h3>'+
                            '<h6 class="doing-item-num">Heading</h6>'+
                            '<div>This is some text inside of a div block.</div>'+
                            '<a class="button doing-item-button" href="#">完成</a>'+
                            '<a class="button doing-item-button-cancel" href="#">X</a>'+
                        '</div>');
            item.data(doing[i]);
            item.find('.doing-item-name').text(doing[i].name);
            item.find('.doing-item-num').text(doing[i].desk+': '+doing[i].num);
            item.find('.doing-item-demand').text(doing[i].demand);

            $('.left-content').append(item);
        }
    }
}