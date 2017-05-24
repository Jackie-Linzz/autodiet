
$(document).ready(function(){

    //get company data
    $.postJSON(
        '/company-data',
        {},
        function(response){
            console.log(response);
            $('.entry-heading').text(response.shortname);
            $('.welcome-p').text(response.welcome);
        }
    );


    // for faculty to login
    $('div.welcome').on('tap', function(){


        window.location.replace('/faculty-login?hh=0');

    });
    //$('#entry').removeClass('ui-page-theme-a');
    //$('#entry').find('*').attr('data-role', 'none');
    //$('.desk-input').parent().removeClass();


//----------------------------------------------------------
    var flag = navigator.getUserMedia  || navigator.mozGetUserMedia || navigator.msGetUserMedia;
    if(flag) {
        $('.qrcode').show();

        $('.manual').hide();
    } else {
        $('.qrcode').hide();
        $('.manual').show();
    }


    $(document).on('tap', '.cover', function(){
        $('.cover').hide();
        $('canvas').css('display', 'block');
        scan();
    });

    $(document).on('tap', '.desk-button',function(e){

        //<a> disabled for 5s
        if(!$(this).data('tapTime')) $(this).data('tapTime', 0);
        if (e.timeStamp < $(this).data('tapTime') + 5000) {
            e.preventDefault();
            return;
        }
        $(this).data('tapTime', e.timeStamp);
        //show tapped effect

        //desk is string, send desk, set cookie who= desk= session=
        var desk = trim($('.desk-input').val());
        if(desk == '') return;
        //alert('tapped');
        transfer(desk);

    });

});

function transfer(desk){
    alert(desk);
    desk = trim(String(desk));
    $.postJSON(
            '/',
            {'desk': json(desk)},
            function(response){
                var next = response.next;
                window.location.replace(next);
            }
        );
}
function parse() {
    alert('parse');
    qrcode.callback = transfer;
    setInterval(function(){
        context.drawImage(video, 0, 0, 200, 200);
        qrcode.decode();
    }, 50);

}

function scan() {
    alert('scan');
    var canvas = document.getElementById("qr-canvas");
    window.context = canvas.getContext("2d");

/*
    var devices = [];
    MediaStreamTrack.getSources(function(sourceInfos) {
        for(var i in sourceInfos) {
            if(sourceInfos[i].kind === 'video') devices.push(sourceInfos[i].id);
        }
        alert('track:'+devices);
    });

*/
    window.video = document.getElementById("video");
    //var	videoObj = { "video": {'optional': [{'sourceId': devices[0]}]} };
    var	videoObj = { "video": true };
/*
    var success = function(stream) {
        alert(devices[0]+':::'+devices[1]);
        if (video.mozSrcObject !== undefined) {
            video.mozSrcObject = stream;
        } else {
            video.src = window.URL && window.URL.createObjectURL(stream) || stream;
            video.play();
        }
    };


 */
    var	err = function(error) {
        alert("Video capture error: ");
        $('.qrcode').hide();
        $('.manual').show();
    };

    // Put video listeners into place
    if(navigator.getUserMedia) { // Standard
        navigator.getUserMedia(videoObj, function(stream) {
            alert('standard');
            video.src = stream;
            video.play();
            parse();
        }, err);
    } else if(navigator.webkitGetUserMedia) { // WebKit-prefixed
        navigator.webkitGetUserMedia(videoObj, function(stream){
            alert('webkit');
            video.src = window.webkitURL.createObjectURL(stream);
            video.play();
            parse();
        }, err);
    }
    else if(navigator.mozGetUserMedia) { // Firefox-prefixed
        navigator.mozGetUserMedia(videoObj, function(stream){
            alert('firefox');
            video.src = window.URL.createObjectURL(stream);
            video.play();
            parse();
        }, err);
    } else if(navigator.msGetUserMedia) {
        navigator.msGetUserMedia(videoObj, function(stream){
            alert('ms');
            video.src = window.msURL.createObjectURL(stream);
            video.play();
            parse();
        }, err );
    }


}

