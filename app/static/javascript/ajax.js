(function($) {
  'use strict';

  var VIEW_URL = "/api/";
  var API_URL = "/api/";

  function viewMyTags (e) {
    $.get(VIEW_URL + 'my_tags', {}, function(response) {
        console.log(response);
    });
  }

  function viewMyFriends (e) {
    $.get(VIEW_URL + 'all_friends', {}, function(response) {
        console.log(response);
    });
  }

  function viewFriendTags (e) {
    var uid = $(e.target).data('uid');
    $.get(VIEW_URL + 'friend_tags', { id: uid }, function(response) {
        console.log(response);
    });
  }

  function viewSearchFriends (e) {
    var $input = $($(e.target).find('input').get(0));
    var keyword = $input.val();
    
    $.get(VIEW_URL + 'search_friends', { keyword: keyword }, function(response) {
        console.log(response);
    });
    return false;
  }

  function viewSearchTags (e) {
    var $input = $($(e.target).find('input').get(0));
    var keyword = $input.val();

    $.get(VIEW_URL + 'search_tags', { keyword: keyword }, function(response) {
        console.log(response);
    });
    return false;
  }

  function viewSearchUserByTag (e) {
    var $input = $($(e.target).find('input').get(0));
    var name = $input.val();

    $.get(VIEW_URL + 'get_taggees', { name: name }, function(response) {
        console.log(response);
    });
    return false;
  }

  function apiAddTag (e) {
    var taggee = $(e.target).data('uid');
    var $input = $($(e.target).find('input').get(0));
    var tag = $input.val();

    $.get(API_URL + 'add_tag', { taggee: taggee, tag: tag }, function(response) {
        console.log(response);
    });
    return false;
  }
  
  function apiDeleteTag (e) {
    var name = e.target.value();
    $.get(API_URL + 'delete_tag', { name: name }, function(response) {
        console.log(response);
    });
  }

  $(document).ready(function() {
    $('#viewMyTags').click(viewMyTags);
    $('#viewMyFriends').click(viewMyFriends);
    $('#viewFriendTags').click(viewFriendTags);
    $('#viewSearchFriends').submit(viewSearchFriends);
    $('#viewSearchTags').submit(viewSearchTags);
    $('#viewSearchUserByTag').submit(viewSearchUserByTag);
    $('#apiAddTag').click(apiAddTag);
    $('#apiDeleteTag').click(apiDeleteTag);
  });

}(jQuery));