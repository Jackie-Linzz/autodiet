$(document).ready(function(){
    //secure cookie: who fid session

    $('.button-other').on('tap', function(){
        window.location.replace('/cook-cook-pad?hh=');
    });

    $('.button-home').on('tap', function(){
        window.location.replace('/faculty-home?hh=');
    });

    $('.button-stop').on('tap', function(e){
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        var ins = {'stop': null};
        $.postJSON(
            '/cook-instruction',
            {'instruction': json(ins)},
            function(response){
                auth(response);
            }
        );
    });
    $('.button-call').on('tap', function(e){
        console.log('button-call tapped');
        //disable for 2s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 2000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        var ins = {'call': 'lelele'};
        $.postJSON(
            '/cook-call',
            {'instruction': json(ins)},
            function(response){
                console.log('called');
                auth(response);
            }
        );
    })
});