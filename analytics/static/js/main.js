

$(document).ready(function(e) {

    $('#webpage-form').on('submit', function() {

        $(".loading").css('display', 'block');

        $.ajax({
                url: '/compare_directly',
                type: 'POST',
                data: $('#webpage-form').serialize(),
                success: function(resp) {
                    $(".loading").css('display', 'none');

                    $( ".content" ).append(resp);
                }
            }
        )

        return false;

    });

})
