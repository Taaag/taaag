(function ($) {
    'use strict';

    var VIEW_URL = "/api/";
    var API_URL = "/api/";

    function viewMyTags(e) {
        $.get(VIEW_URL + 'my_tags', {}, function (response) {
            console.log(response);
        });
    }

    function viewMyFriends(e) {
        $.get(VIEW_URL + 'all_friends', {}, function (response) {
            console.log(response);
        });
    }

    function viewFriendTags(e) {
        var uid = $(e.target).data('uid');
        $.get(VIEW_URL + 'friend_tags', {id: uid}, function (response) {
            console.log(response);
        });
    }

    function viewSearchFriends(e, keyword) {
        if (keyword !== '' && !keyword) {
            var $input = $($(e.target).find('input').get(0));
            keyword = $input.val();
        }

        $.get(VIEW_URL + 'search_friends', {keyword: keyword}, function (response) {
            console.log(response);
        });
        return false;
    }

    function viewSearchTags(e, keyword) {
        if (keyword !== '' && !keyword) {
            var $input = $($(e.target).find('input').get(0));
            keyword = $input.val();
        }

        $.get(VIEW_URL + 'search_tags', {keyword: keyword}, function (response) {
            console.log(response);
        });
        return false;
    }

    function viewSearchUserByTag(e) {
        var $input = $($(e.target).find('input').get(0));
        var name = $input.val();

        $.get(VIEW_URL + 'get_taggees', {name: name}, function (response) {
            console.log(response);
        });
        return false;
    }

    function apiAddTag(e) {
        var $form = $(e.target);
        var taggee = $form.data('uid');
        var $input = $($form.find('input').get(0));
        var tag = $input.val();
        console.log('fsa');

        $.get(API_URL + 'add_tag', {taggee: taggee, tag: tag}, function (response) {
            console.log(response);
        });
        return false;
    }

    function apiDeleteTag(e) {
        var $input = $($(e.target).find('input').get(0));
        var name = $input.val();
        $.get(API_URL + 'delete_tag', {name: name}, function (response) {
            console.log(response);
        });
        return false;
    }

    function globalSearch(e) {
        var $input = $($(e.target).find('input').get(0));
        var content = $input.val();
        var firstChar, keyword;

        if (content.length >= 1) {
            firstChar = content[0];
            keyword = content.substring(1);
            if (firstChar === '@') {
                viewSearchFriends(e, keyword);
            } else if (firstChar === '#') {
                viewSearchTags(e, keyword);
            } else {
                console.log('Input must begin with @ or #');
            }
        } else {
            console.log('Empty input');
        }
        return false;
    }

    $(document).ready(function () {
        $('#viewMyTags').click(viewMyTags);
        $('#viewMyFriends').click(viewMyFriends);
        $('#viewFriendTags').click(viewFriendTags);
        $('#viewSearchFriends').submit(viewSearchFriends);
        $('#viewSearchTags').submit(viewSearchTags);
        $('#viewSearchUserByTag').submit(viewSearchUserByTag);
        $('#apiAddTag').submit(apiAddTag);
        $('#apiDeleteTag').submit(apiDeleteTag);

        $('#global-search-form').submit(globalSearch);
    });

}(jQuery));