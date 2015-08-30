(function ($) {
    'use strict';

    var loading = '<div class="spinner"></div>';

    var historyStack = [];
    var futureStack = [];
    var currentView;

    function loadView(view, data) {
        currentView = [view, data];
        $('#content-view').html(loading);
        $.get('/change_view/' + view, data, function (response) {
            $('#content-view').html(response);
            $('#search-bar').typeahead('val', '');
            $('.tooltip').remove();
        });
    }

    $(document).on("viewChanging", function (event, view, data) {
        historyStack.push(currentView);
        futureStack = [];
        console.log(futureStack);
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
        $('#menu-friends').click(function () {
            $(document).trigger("viewChanging", ["friends", {}]);
        });
        $('#back-btn').click(function () {
            if (historyStack.length > 0) {
                var data = historyStack.pop();
                futureStack.push(currentView);
                loadView(data[0], data[1]);
            }
        });
        $('#forward-btn').click(function () {
            if (futureStack.length > 0) {
                var data = futureStack.pop();
                historyStack.push(currentView);
                loadView(data[0], data[1]);
            }
        });
        $('#like-btn').click(function () {
            FB.ui({
                method: 'share_open_graph',
                action_type: 'og.likes',
                action_properties: JSON.stringify({
                    object: 'https://apps.facebook.com/687248731410966',
                })
            }, function (response) {
            });
        });
        $('#invite-btn').click(function () {
            FB.ui({
                method: 'apprequests',
                filters: ['app_non_users'],
                message: 'Come and join Taaag to tag your friends!'
            }, function (response) {
                $.bootstrapGrowl('Successfully invited ' + response.to.length.toString() + ' friends.');
            });
        });
        $('.friendlist-friend').click(function() {
            var uid = $(this).attr('data-uid');
            $(document).trigger('viewChanging', ['friend', uid])
        });
    });
}(jQuery));
