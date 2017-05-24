$(document).ready(function(){
    //cookie


    // hover event
    $('.nav-item').on('mouseenter', function(){
        $(this).find('.nav-item-content').show();
        $(this).css('background-color', '#9cf');
        $(this).find('.nav-item-content').css('background-color', '#9cf');
    });
    $('.nav-item').on('mouseleave', function(){
        $(this).find('.nav-item-content').hide();
        $(this).css('background-color', 'transparent');

    });
    $('.manager-content').children().hide();
    //show respective div
    $('#info-link').on('tap', function(){

        $('.manager-content').children().hide();
        $('.company-info').show();
    });
    $('#category-link').on('tap', function(){
        $('.manager-content').children().hide();
        $('.category-manage').show();
    });
    $('#diet-link').on('tap',function(){
        $('.manager-content').children().hide();
        $('.diet-manage').show();
    });
    $('#desk-link').on('tap', function(){
        $('.manager-content').children().hide();
        $('.desk-manage').show();
    });

    $('#faculty-link').on('tap',function(){
        $('.manager-content').children().hide();
        $('.faculty-manage').show();
    });
    $('#history-link').on('tap', function(){
        $('.manager-content').children().hide();
        $('.history').show();
    });




    //category new submit  in form not ajax
    //event category-refresh button
    $('.category-refresh').on('tap', function(){
        $.ajax({
            url: 'category-manage',
            type: 'GET',
            data: {},
            dataType: 'json',
            success: function(response) {
                console.log(response);
                window.categories = response.categories;
                showCategories(categories);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });
    //event category-del button
    $(document).on('tap', '#current-category .button-del', function(){
        var item = $(this).parents('tr');
        var cid = item.data('id');
        $.postJSON(
            '/category-manage',
            {'cid': json(cid)},
            function(response) {
                window.categories = response.categories;
                showCategories(categories);
            }
        )
    });
    //diet new submit in form not in ajax
    //event diet-refresh button
    $('.diet-refresh').on('tap', function(){
        $.ajax({
            url: 'diet-manage',
            type: 'GET',
            data: {},
            dataType: 'json',
            success: function(response) {
                console.log(response);
                window.diet = response.diet;
                showDiet(diet);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });
    //event diet-del button
    $(document).on('tap', '#current-diet .button-del', function(){
        var item = $(this).parents('tr');
        var id = item.data('id');
        $.postJSON(
            '/diet-manage',
            {'id': json(id)},
            function(response) {
                console.log(response);
                window.diet = response.diet;
                showDiet(diet);
            }
        )
    });

    //event desk-button tapped
    $('.desk-button').on('tap', function(){
        var desk = trim($('.desk-input').val());
        if(desk == '') return;
        $.postJSON(
            '/desk-add',
            {'desk': json(desk)},
            function(response) {
                console.log(response);
                window.desks = response.desks;
                showDesk(desks);
            }
        );

    });
    $('.desks-refresh').on('tap', function(){
        $.ajax({
            url: 'desk-manage',
            type: 'GET',
            data: {},
            dataType: 'json',
            success: function(response) {
                console.log(response);
                window.desks = response.desks;
                showDesk(desks);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

    //event desk-item-del tapped
    $(document).on('tap', '.desk-item-del', function(){
        var item = $(this).parents('.desk-item');
        var desk = trim(item.data('desk'));
        $.postJSON(
            '/desk-manage',
            {'desk': json(desk)},
            function(response){
                console.log(response);
                window.desks = response.desks;
                showDesk(desks);
            }
        );
    });
    //event qrcode download
    $('.qrcode-download').on('tap', function(){
        $.postJSON(
            '/qrcode-download',
            {},
            function(){}
        );
    });

    //event faculty-refresh button
    $('.faculty-refresh').on('tap', function(){
         $.ajax({
            url: 'faculty-manage',
            type: 'GET',
            data: {},
            dataType: 'json',
            success: function(response) {
                console.log(response);
                window.faculty = response.faculty;
                showFaculty(faculty);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });
    //event faculty del button
    $(document).on('tap', '#current-faculty .button-del', function(){
        var item = $(this).parents('tr');
        var id = item.data('id');
        $.postJSON(
            '/faculty-manage',
            {'id': json(id)},
            function(response){
                window.faculty = response.faculty;
                showFaculty(faculty);
            }
        )
    });
    $('.history-button').on('tap', function(){
        var year_from = trim($('.year_from').val());
        var month_from = trim($('.month_from').val());
        var day_from= trim($('.day_from').val());
        var year_to = trim($('.year_to').val());
        var month_to = trim($('.month_to').val());
        var day_to= trim($('.day_to').val());

        $.postJSON(
            '/history-data',
            {'year_from': json(year_from), 'month_from': json(month_from), 'day_from': json(day_from),
             'year_to': json(year_to), 'month_to': json(month_to), 'day_to': json(day_to)},
            function(response) {
                console.log(response);
                window.diet_stat = response.diet_stat;
                window.cook_stat = response.cook_stat;
                window.trend_stat = response.trend_stat;
                showDietStat(diet_stat);
                showCookStat(cook_stat);
                showTrend(trend_stat);

            }
        );


    });
});

function showCategories(categories){
    var p = $('#current-category tbody').empty();
    for(var i in categories) {
        var item = $('<tr>'+
                        '<td><p class="id">id</p></td>'+
                        '<td><p class="name">name</p></td>'+
                        '<td><p class="order">order</p></td>'+
                        '<td><p class="desc">desc</p></td>'+
                        '<td><a href="javascript:void(0)" class="picture">查看</a></td>'+
                        '<td><a href="javascript:void(0)" class="button-del">X</a> </td>'+
                    '</tr>');
        item.data(categories[i]);
        item.find('.id').text(categories[i].id);
        item.find('.name').text(categories[i].name);
        item.find('.order').text(categories[i].ord);
        item.find('.desc').text(categories[i].description);
        item.find('.picture').attr('href', '/static/pictures/'+categories[i].picture);
        if(categories[i].picture == '') item.find('.picture').text('');
        p.append(item);

    }

}

function showDiet(diet){
    var p = $('#current-diet tbody').empty();
    for(var i in diet) {
        var item = $('<tr>'+
                        '<td><p class="id">d</p></td>'+
                        '<td><p class="name">d</p></td>'+
                        '<td><p class="price">d</p></td>'+
                        '<td><p class="base">d</p></td>'+
                        '<td><p class="cid">d</p></td>'+
                        '<td><p class="order">d</p></td>'+
                        '<td><input type="text" class="desc"/></td>'+
                        '<td><a href="javascript:void(0)" class="picture">查看</a> </td>'+
                        '<td><a href="javascript:void(0)" class="button-del">X</a> </td>'+
                    '</tr>');
        item.data(diet[i]);
        item.find('.id').text(diet[i].id);
        item.find('.name').text(diet[i].name);
        item.find('.price').text(diet[i].price);
        item.find('.base').text(diet[i].base);
        item.find('.cid').text(diet[i].cid);
        item.find('.order').text(diet[i].ord);
        item.find('.desc').val(diet[i].description);
        item.find('.picture').attr('href', '/static/pictures/'+diet[i].picture);
        if(diet[i].picture == '') item.find('.picture').remove();
        p.append(item);

    }
}

function showDesk(desks) {
    var p = $('#current-desks').empty();
    for(var i in desks) {
        var item = $('<div class="desk-item">'+
                        '<h4 class="desk-item-heading">num</h4>'+
                        '<img src="/static/pictures/xia.jpg" alt="no image" class="desk-item-image"/>'+
                        '<a href="javascript:void(0)" class="desk-item-del">删除</a>'+
                    '</div>');
        item.data('desk', desks[i]);
        item.find('.desk-item-heading').text(desks[i]);
        item.find('img').attr('src', '/static/desks/'+desks[i]+'.png');
        p.append(item);
    }
}

function showFaculty(faculty){
    var p = $('#current-faculty tbody').empty();
    for(var i in faculty) {
        var item = $('<tr>'+
                        '<td><p class="id">1</p></td>'+
                        '<td><p class="name">2</p></td>'+
                        '<td><p class="role">3</p></td>'+
                        '<td><p class="password">4</p></td>'+
                        '<td><a href="javascript:void(0)" class="button-del">X</a></td>'+
                    +'</tr>');
        item.data(faculty[i]);
        item.find('.id').text(faculty[i].id);
        item.find('.name').text(faculty[i].name);
        item.find('.role').text(faculty[i].role);
        item.find('.password').text(faculty[i].password);
        p.append(item);

    }

}



function showDietStat(stat) {
    var p = $('#order-detail tbody').empty();

    var total = stat[0];
    var detail = stat[1];

    for(var i in detail) {
        var item = $('<tr>'+
                        '<td><p class="id">1</p></td>'+
                        '<td><p class="name">2</p></td>'+
                        '<td><p class="price"></p>'+
                        '<td><p class="num">3</p></td>'+
                        '<td><p class="val">4</p></td>'+

                        '<td><p class="percent">6</p></td>'+

                    '</tr>');
        item.find('.id').text(detail[i].id);
        item.find('.name').text(detail[i].name);
        item.find('.price').text(detail[i].price);
        item.find('.num').text(detail[i].num);
        item.find('.val').text(detail[i].price * detail[i].num);
        var percent = detail[i].price * detail[i].num / total * 100;
        item.find('.percent').text(Math.round(percent * 100)/100 + '%');
        if(total == 0) item.find('.percent').text(0);
        p.append(item);

    }
    var last_item = $('<tr><td></td><td></td><td></td><td></td><td><p class="total"></p></td><td></td></tr>');
    last_item.find('.total').text(total);
    p.append(last_item);
}

function showCookStat(stat) {
    var total = stat[0];
    var detail = stat[1];

    var p = $('#cook-detail tbody').empty();
    for(var i in detail) {
        var item = $('<tr>'+
                        '<td><p class="fid">1</p></td>'+
                        '<td><p class="name">2</p></td>'+

                        '<td><p class="num">4</p></td>'+
                        '<td><p class="val">5</p></td>'+
                        '<td><p class="percent">6</p></td>'+

                    '</tr>');
        item.find('.fid').text(detail[i].fid);
        item.find('.name').text(detail[i].name);

        item.find('.num').text(detail[i].num);
        item.find('.val').text(detail[i].val);
        var percent = detail[i].val / total * 100;
        item.find('.percent').text(Math.round(percent*100)/100 + '%');
        if(total == 0) item.find('.percent').text(0);
        p.append(item);

    }
    var last_item = $('<tr><td></td><td></td><td></td><td><p class="total"></p></td><td></td></tr>');
    last_item.find('.total').text(total);
    p.append(last_item);
}

function showTrend(trend) {

    var diet_trend = trend.diet_stat;
    var cook_trend = trend.cook_stat;

    names = [];
    diet_trend_data = [];
    cook_trend_data = [];
    for(var i in diet_trend) {
        names.push(diet_trend[i].stamp_from);
        diet_trend_data.push(diet_trend[i].vals);
        cook_trend_data.push(cook_trend[i].vals);

    }
    var barChartData = {
        labels: names,
        datasets: [
            {
                fillColor : "rgba(220,220,220,0.5)",
				strokeColor : "rgba(220,220,220,0.8)",
				highlightFill: "rgba(220,220,220,0.75)",
				highlightStroke: "rgba(220,220,220,1)",
                data: diet_trend_data
            },
            {
                fillColor : "rgba(151,187,205,0.5)",
				strokeColor : "rgba(151,187,205,0.8)",
				highlightFill : "rgba(151,187,205,0.75)",
				highlightStroke : "rgba(151,187,205,1)",
                data: cook_trend_data
            }
        ]

    };
    var ctx = document.getElementById("trend").getContext("2d");
    window.myBar = new Chart(ctx).Bar(barChartData, {
        responsive : true
    });
}

function testChart() {
    var randomScalingFactor = function(){ return Math.round(Math.random()*100)};

	var barChartData = {
		labels : ["January","February","March","April","May","June","July"],
		datasets : [
			{
				fillColor : "rgba(220,220,220,0.5)",
				strokeColor : "rgba(220,220,220,0.8)",
				highlightFill: "rgba(220,220,220,0.75)",
				highlightStroke: "rgba(220,220,220,1)",
				data : [randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor()]
			},
			{
				fillColor : "rgba(151,187,205,0.5)",
				strokeColor : "rgba(151,187,205,0.8)",
				highlightFill : "rgba(151,187,205,0.75)",
				highlightStroke : "rgba(151,187,205,1)",
				data : [randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor()]
			}
		]

	};

    var ctx = document.getElementById("trend").getContext("2d");
    window.myBar = new Chart(ctx).Bar(barChartData, {
        responsive : true
    });


}