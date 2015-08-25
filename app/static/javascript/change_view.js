(function ($) {
    'use strict';

    function loadView(view, data) {
        $.get('/change_view/' + view, data, function (response) {
            $('#content-view').html(response);
        });
    }

    $(document).on("viewChanging", function (event, view, data) {
        loadView(view, data);
    });

    $(document).ready(function () {
        loadView('index', {});
        $('.to-home').click(function () {
            loadView('index', {});
        });
    });
}(jQuery));
