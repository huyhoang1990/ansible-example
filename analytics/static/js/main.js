

$(document).ready(function(e) {

    $('#httper').on('submit', function() {
//        $('#httper').find('button')[0].type = 'button';

        var scores = ['pagespeed_score', 'yslow_score',
            'page_size', 'total_request', 'location']


        for (var index in scores) {
            var class_name = '.' + scores[index];
            console.log(class_name);
            $(class_name).empty();
            $(class_name).append('Checking...');
        }

        $.ajax({
                url: '/',
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
