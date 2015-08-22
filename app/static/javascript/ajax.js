(function($) {
  'use strict';

  var VIEW_URL = "/view";
  var API_URL = "/api";

  function viewMyTags (e) {
    var data = { target: "user", method: "my_tags" };
    $.get(VIEW_URL, data, function(response) {
        console.log(response);
    });
  }

  function viewFriendTags (e) {
    var uid = e.target.dataUid();
    var data = { target: "user", method: "friend_tags", uid: uid };
    $.get(VIEW_URL, data, function(response) {
        console.log(response);
    });
  }

  function viewSearchFriends (e) {
    var name = e.target.value();
    var data = { target: "user", method: "search_friends", name: name };
    $.get(API_URL, data, function(response) {
        console.log(response);
    });
  }

  function viewSearchTags (e) {
    var name = e.target.value();
    var data = { target: "tag", method: "search_tags", name: name };
    $.get(API_URL, data, function(response) {
        console.log(response);
    });
  }

  function viewSearchUserByTag (e) {
    var name = e.target.value();
    var data = { target: "tag", method: "get_taggees", name: name };
    $.get(API_URL, data, function(response) {
        console.log(response);
    });
  }
  
  function apiAddTag (e) {
    var uid = e.target.dataUid();
    var name = e.target.value();
    var data = { target: "user", method: "add_tag", taggee: uid, name: name };
    $.get(API_URL, data, function(response) {
        console.log(response);
    });
  }
  
  function apiDeleteTag (e) {
    var name = e.target.value();
    var data = { target: "user", method: "delete_tag", name: name };
    $.get(API_URL, data, function(response) {
        console.log(response);
    });
  }

  $(document).ready(function() {
    $('#my-tags').click(viewMyTags());
  });

}(jQuery));