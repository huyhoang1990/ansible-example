

$(document).ready(function(e) {

    $('#httper').on('submit', function() {
//        $('#httper').find('button')[0].type = 'button';

        var scores = ['pagespeed_score', 'yslow_score',
            'page_size', 'total_request', 'location']

        var path_name = window.location.pathname;

        for (var index in scores) {
            if (path_name == '/'){
                var class_name = '.' + scores[index];
                $(class_name).empty();
                $(class_name).append('Checking...');
            }

            if (path_name == '/powerup') {
                var filmtrip_loading = $('.filmstrip-loading').css('display', 'block');
                var class_name_1 = '.' + scores[index] + '1';
                var class_name_2 = '.' + scores[index] + '2';
                $(class_name_1).empty();
                $(class_name_2).empty();
                $(class_name_1).append('Checking...');
                $(class_name_2).append('Checking...');
            }

        }

        $.ajax({
                url: path_name,
                type: 'POST',
                data: $('#httper').serialize(),

                success: function(resp) {
                    $("#results").empty();
                    $("#results").append(resp);
                }

            }
        )

        return false;

    });





})
