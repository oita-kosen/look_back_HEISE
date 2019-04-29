$(document).ready(function() {
    namespace = '/test'; //main.pyで指定したnamespace
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    var letter_count = 30;
    var card_count = 0;
	var maxcards = 3;
	var flag = 0;
    //テキストエリアはこちらで受信。main.py側からmy_content宛に送られたデータを受け取る
    socket.on('my_content', function(msg) {
        var title = msg.title;
        //var letter_count = 30;
        var length = title.length;
        if(length > letter_count){
            title = title.substring(0,letter_count);
            title += '...';
        }
        PlaySound();

        card_count++;
        if(msg.genre.match('twitter')){
            $(".row").prepend('<div class="col-xs-12 col-sm-4"><div class="card twitter_card id=card_'+card_count+'"><a class="img-card" href="'+ msg.url +'" target="_blank"><img src="'+msg.img+'" /></a><div class="card-content"><h4 class="card-title"><a href="'+ msg.url +'" target="_blank">' + title + '</a></h4><table  class="t12 font12"><tr><td class="table-title">ジャンル</td><td>：</td><td class="genre">'+ msg.genre +'</td></tr><tr><td class="table-title">日付</td><td>：</td><td class="date">'+ msg.date +'</td></tr></table></div><div class="card-read-more"><a href="'+ msg.url +'" class="btn btn-link btn-block" target="_blank">Read More</a></div></div></div>'); 
        }else if(msg.genre.match("これから")){
            $(".row").prepend('<div class="col-xs-12 col-sm-4"><div class="card reiwa_card id=card_'+card_count+'"><a class="img-card" href="'+ msg.url +'" target="_blank"><img src="'+msg.img+'" /></a><div class="card-content"><h4 class="card-title reiwa"><a href="'+ msg.url +'" target="_blank">' + title + '</a></h4><table  class="t12 font12_reiwa"><tr><td class="table-title">ジャンル</td><td>：</td><td class="genre">'+ msg.genre +'</td></tr><tr><td class="table-title">日付</td><td>：</td><td class="date">'+ msg.date +'</td></tr></table></div><div class="card-read-more"><a href="'+ msg.url +'" class="btn btn-link btn-block reiwa" target="_blank">Read More</a></div></div></div>');
        }
        else{
            $(".row").prepend('<div class="col-xs-12 col-sm-4"><div class="card id=card_'+card_count+'"><a class="img-card" href="'+ msg.url +'" target="_blank"><img src="'+msg.img+'" /></a><div class="card-content"><h4 class="card-title"><a href="'+ msg.url +'" target="_blank">' + title + '</a></h4><table  class="t12 font12"><tr><td class="table-title">ジャンル</td><td>：</td><td class="genre">'+ msg.genre +'</td></tr><tr><td class="table-title">日付</td><td>：</td><td class="date">'+ msg.date +'</td></tr></table></div><div class="card-read-more"><a href="'+ msg.url +'" class="btn btn-link btn-block" target="_blank">Read More</a></div></div></div>'); 
        }

        var fadein_id = '#card_'+card_count;
		var anim = anime.timeline();
		anim.add({
			targets: fadein_id,
			translateX: -400,
			duration: 0
		});

		anim.add({
			targets: fadein_id,
			translateX: 0,
			duration: 300,
			loop: false,
			direction: 'alternate',
			easing: 'easeOutElastic(1, 0.8)'
        });

        $('.card').each(function(){
			var index =$('.card').index(this); //何番目か
			if(flag == 0){
				if(index >= maxcards){
					$(this).addClass('disnone');
					$('.more').removeClass('disnone');
				}
			}
		});
    });

    //htmlのフォームがsubmitされた時に、main.pyのreceive_content宛にテキストエリアのid="input_data"の値を送信します。
    $('form#broadcast').submit(function(event) {
        socket.emit('my_broadcast_event',{event:"news"});
        console.log("protocol" + ':' + location.protocol);
        console.log("domain" + ':' + document.domain);
        console.log("port" + ':' + location.port);
        return false;
    });
    $('form#twitter').submit(function(event) {
        socket.emit('my_broadcast_event',{event:"twitter"});
        console.log("protocol" + ':' + location.protocol);
        console.log("domain" + ':' + document.domain);
        console.log("port" + ':' + location.port);
        return false;
    });
    $('form#reiwa').submit(function(event) {
        socket.emit('my_broadcast_event',{event:"reiwa"});
        console.log("protocol" + ':' + location.protocol);
        console.log("domain" + ':' + document.domain);
        console.log("port" + ':' + location.port);
        return false;
    });
    $('#more').click(function () { 
		$('.card').each(function(){
			var index =$('.card').index(this); //何番目か
			if(index >= maxcards){
				$(this).removeClass('disnone');
				$('.more').addClass('disnone');
				$('.cl').removeClass('disnone');
				flag = 1;
			}
		});
	});
	$('#close').click(function () { 
		$('.card').each(function(){
			var index =$('.card').index(this); //何番目か
			if(index >= maxcards){
				$(this).addClass('disnone');
				$('.more').removeClass('disnone');
				$('.cl').addClass('disnone');
				flag = 0;
			}
		});
    });
    var TopBtn = $('#PageTopBtn');    
    TopBtn.hide();
    // スクロール位置が100でボタンを表示
    $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
            TopBtn.fadeIn();
        } 
        else {
            TopBtn.fadeOut();
        }
    });
    // ボタンを押下するとトップへ移動
    TopBtn.click(function() {
        $('body,html').animate({
            scrollTop: 0
        }, 300);
        return false;
    });
});

var audioElem;
function PlaySound() {
    audioElem = new Audio();
    audioElem.src = "/static/sound/text-impact.mp3";
    audioElem.volume = 0.2;
    audioElem.play();
}
function StopSound(){
    audioElem.pause();
}