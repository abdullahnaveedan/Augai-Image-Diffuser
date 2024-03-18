$(document).ready(function () {
    $('.check').hide();
    $('#user_input').on('input', function () {
        var inputLength = $(this).val().length;
        var counter = $('#counter');
        var alertBox = $('#valueAlert');

        if (inputLength <= 999) {
            counter.text(inputLength + ' / 999');
            alertBox.addClass('d-none');
        } else {
            counter.text((999) + ' / 999');
            alertBox.removeClass('d-none');
            $(this).val($(this).val().substring(0, 999));
        }
    });
});

$('#language_translate').submit(function (event) {
    event.preventDefault();
    var spinner = $('.spinner');
    var enter = $('.bi-arrow-90deg-right');
    enter.addClass('d-none');
    spinner.removeClass('d-none');
    $.ajax({
        url: '/language-translator/',
        type: 'POST',
        data: $(this).serialize(),
        success: function (response) {
            console.log(response.status);
            spinner.addClass('d-none');
            enter.removeClass('d-none');
            var output = $('#output_text');
            output.html('');

            $('#output_text').val(response.message);
        },error: function(error){
            console.error(error);
        }
    });
});
function hideCheck(){
    $('.check').hide();
    $('.clipboard').show();
}
function language_convertor(){
    var input = $('.input_lang').val();  
    var output = $('.output_lang').val();
    $('.input_lang').val(output);
    $('.output_lang').val(input);
    var inputText = $('#user_input').val();
    var outputText = $('#output_text').val();
    $('#user_input').val(outputText);
    $('#output_text').val(inputText);  
}

function copy_clipboard(){
    $('.check').show();
    $('.clipboard').hide();
    setTimeout(hideCheck , 3000);
    var copyText = document.getElementById("output_text");
    navigator.clipboard.writeText(copyText.value);
}
function copyBtn() {
    var btn = $('.copybtn');
    btn.removeClass('pe-none');
}