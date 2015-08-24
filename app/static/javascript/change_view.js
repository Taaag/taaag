(function ($) {
    'use strict';

    var VIEW_URL = "/api/";
    var API_URL = "/api/";

    function loadView(view, data) {
        $.get('/change_view/' + view, data, function(response) {
            $('#content-view').html(response);
        });
    }

    $(document).ready(function () {
        loadView('index', {});
    });
}(jQuery));