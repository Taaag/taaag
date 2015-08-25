(function ($) {
    'use strict';

    var loading = '<div class="inner-circles-loader">Loading…</div>';

    var historyStack = [];

    function loadView(view, data) {
        historyStack.push([view, data]);
        $('#content-view').html(loading);
        $.get('/change_view/' + view, data, function (response) {
            $('#content-view').html(response);
            $('#search-bar').typeahead('val', '');
        });
    }

    $(document).on("viewChanging", function (event, view, data) {
        loadView(view, data);
    });

    $('#back-btn').click(function () {
        var data = historyStack.pop();
        loadView(data[0], data[1]);
    });

    $(document).ready(function () {
        loadView('index', {});
        $('.to-home').click(function () {
            loadView('index', {});
        });
        $('#menu-me').click(function () {
            loadView('me', {});
        });
    });
}(jQuery));
