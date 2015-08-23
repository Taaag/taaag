(function ($) {
    'use strict';
    $(document).ready(function () {
        $("#menu").mouseover(function () {
            console.log('sf');
            $("#menu-items").stop().slideDown("slow");
        });
        $("#menu").mouseout(function () {
            $("#menu-items").slideUp("slow");
        });
    });
}(jQuery));