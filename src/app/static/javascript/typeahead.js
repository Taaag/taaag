(function ($) {
    'use strict';

    $(function () {
        var friends = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            prefetch: {
                url: '/api/all_friends',
                cache: false,
                transform: function (response) {
                    return response['response']
                }
            }
        });

        var tags = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.whitespace,
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            prefetch: {
                url: '/api/all_tags',
                cache: false,
                transform: function (response) {
                    return response['response']
                }
            }
        });

        var invitable_friends = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            prefetch: {
                url: '/api/invitable_friends',
                cache: false,
                transform: function (response) {
                    return response['response']
                }
            }
        });

        $('#search-bar').typeahead({highlight: true, hint: false},
            {
                name: 'tags',
                source: tags,
                templates: {
                    header: '<h3>Tags</h3>'
                }
            }, {
                name: 'friends',
                source: friends,
                display: 'name',
                templates: {
                    header: '<h3>Friends</h3>',
                    suggestion: function (friend) {
                        return '<div>' + friend.name + '</div>';
                    }
                }
            }, {
                name: 'invitable_friends',
                source: invitable_friends,
                display: 'name',
                templates: {
                    suggestion: function (friend) {
                        return '<div>' + friend.name + '</div>';
                    }
                }
            });

        $('.typeahead').bind('typeahead:select', function (ev, suggestion) {
            if (suggestion.hasOwnProperty('picture')) {
                $('#invite-btn').click(function () {
                    FB.ui({
                        method: 'apprequests',
                        to: suggestion['id'],
                        message: 'Come and join Taaag to tag your friends!'
                    }, function (response) {
                        $.bootstrapGrowl('Successfully invited ' + response.to.length.toString() + ' friends.');
                    });
                });
            } else if (suggestion.hasOwnProperty('name')) {
                $(document).trigger("viewChanging", ["friend", {'id': suggestion['id']}]);
            } else {
                $(document).trigger("viewChanging", ["tag", {'name': suggestion}]);
            }
        });
    });
}(jQuery));