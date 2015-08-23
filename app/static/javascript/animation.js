(function ($) {
    'use strict';
    $(document).ready(function () {
        $("#menu").mouseover(function () {
            $("#menu-items").stop().slideDown("fast");
        });
        $("#menu").mouseout(function () {
            $("#menu-items").stop().slideUp("fast");
        });

        $(window).resize(function () {
            console.log('dsf');
            if($(this).width() <= 360) {
                $("#logo-container").hide()；
            }
        });
    });
}(jQuery));