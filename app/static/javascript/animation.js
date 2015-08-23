(function ($) {
    'use strict';
    $(document).ready(function () {
        $("#menu").mouseover(function () {
            $("#menu-items").stop().slideDown("fast");
        });
        $("#menu").mouseout(function () {
            $("#menu-items").stop().slideUp("fast");
        });
    });
}(jQuery));