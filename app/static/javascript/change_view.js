(function ($) {
    'use strict';

    var loading = '<div class="inner-circles-loader">Loading…</div>';

    var historyStack = [];
    var currentView;

    function loadView(view, data) {
        currentView = [view, data];
        $('#content-view').html(loading);
        $.get('/change_view/' + view, data, function (response) {
            $('#content-view').html(response);
            $('#search-bar').typeahead('val', '');
        });
    }

    $(document).on("viewChanging", function (event, view, data) {
        historyStack.push(currentView);
        loadView(view, data);
    });

    $(document).ready(function () {
        loadView("index", {});
        $('.to-home').click(function () {
            $(document).trigger("viewChanging", ["index", {}]);
        });
        $('#menu-me').click(function () {
            $(document).trigger("viewChanging", ["me", {}]);
        });
        $('#menu-settings').click(function () {
            $(document).trigger("viewChanging", ["manage", {}]);
        });
        $('#back-btn').click(function () {
            var data = historyStack.pop();
            loadView(data[0], data[1]);
        });
    });
}(jQuery));
