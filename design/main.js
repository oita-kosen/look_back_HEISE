$(document).ready(function() {

    //htmlのフォームがsubmitされた時に、main.pyのreceive_content宛にテキストエリアのid="input_data"の値を送信します。
    $('form#broadcast').submit(function(event) {
        var title = $('#data').val();
        var count = 30;
        var length = title.length;
        if(length > count){
            title = title.substring(0,count);
            title += '...';
        }
        console.log(title);
    });
});