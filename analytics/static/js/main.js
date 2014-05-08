

$(document).ready(function(e) {

    $('#webpage-form').on('submit', function() {

        $(".content").empty();
        $(".loading").css('display', 'block');

        $.ajax({
                url: '/compare_directly',
                type: 'POST',
                data: $('#webpage-form').serialize(),
                success: function(resp) {
                    $(".loading").css("display", "none");

                    $(".content").append(resp);
                }
            }
        )

        return false;

    });


    $('#powerup-form').on('submit', function() {

        $(".content-powerup").empty();
        $(".loading").css('display', 'block');

        $.ajax({
                url: '/compare',
                type: 'POST',
                data: $('#powerup-form').serialize(),

                success: function(resp) {
                    $(".loading").css('display', 'none');

                    $( ".content-powerup" ).append(resp);
                }

            }
        )

        return false;

    });



    $('#httper').on('submit', function() {
        $('#httper').find('button')[0].type = 'button';
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
