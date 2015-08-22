(function($) {
  'use strict';

  var myTagUrl = "/api";

  $(document).ready(function() {
    console.log('wtf');

    $('button').click(function() {
        console.log('wtf');
    });

    $('#my-tags').click(function() {
        $.ajax({
          type: 'GET',
          url: myTagUrl,
          data: {
            target: "user",
            method: "my_tags"
          },
          success: function(response) {
            console.log(response);
          }
        });
    });
  });



}(jQuery));