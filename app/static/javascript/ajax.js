(function($) {
  'use strict';

  var VIEW_URL = "/view/";
  var API_URL = "/api/";

  function viewMyTags (e) {
    $.get(VIEW_URL + 'my_tags', {}, function(response) {
        console.log(response);
    });
  }

  function viewFriendTags (e) {
    var uid = e.target.dataUid();
    $.get(VIEW_URL + 'friend_tags', { id: id }, function(response) {
        console.log(response);
    });
  }

  function viewSearchFriends (e) {
    var keyword = e.target.value();
    $.get(VIEW_URL + 'search_friends', { keyword: keyword }, function(response) {
        console.log(response);
    });
  }

  function viewSearchTags (e) {
    var keyword = e.target.value();
    $.get(VIEW_URL + 'search_tags', { keyword: keyword }, function(response) {
        console.log(response);
    });
  }

  function viewSearchUserByTag (e) {
    var name = e.target.value();
    $.get(API_URL + 'get_taggees', { name: name }, function(response) {
        console.log(response);
    });
  }

  function apiAddTag (e) {
    var taggee = e.target.dataUid();
    var tag = e.target.value();
    $.get(API_URL + 'add_tag', { taggee: taggee, tag: tag }, function(response) {
        console.log(response);
    });
  }
  
  function apiDeleteTag (e) {
    var name = e.target.value();
    $.get(API_URL + 'delete_tag', { name: name }, function(response) {
        console.log(response);
    });
  }

  $(document).ready(function() {
    $('#my-tags').click(viewMyTags());
  });

}(jQuery));