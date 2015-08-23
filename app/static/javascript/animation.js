(function ($) {
    'use strict';

    function showOrHideLogo() {
        var width = $(window).width();
        console.log(width);
        if (width <= 360) {
            $("#logo-container").hide();
        } else {
            $("#logo-container").show();
        }
    }

    function toggleMenu() {
        $("#menu").mouseover(function () {
            $("#menu-items").stop().slideDown("fast");
        });
        $("#menu").mouseout(function () {
            $("#menu-items").stop().slideUp("fast");
        });
    }

    $(document).ready(function () {
        showOrHideLogo();

        toggleMenu();

        $(window).resize(showOrHideLogo);
    });
}(jQuery));