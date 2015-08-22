(function($) {
  'use strict';

  var myTagUrl = "/api";

  $(document).ready(function() {
    $('#my-tags').click(function() {
        $.get(myTagUrl,
          {
            target: "user",
            method: "my_tags"
          },
          function(response) {
            console.log(response);
          });
    });
  });



}(jQuery));