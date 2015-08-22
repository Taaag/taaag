(function($) {
  'use strict';

  function query(method)

  var myTagUrl = "/api";

  $(document).ready(function() {
    console.log('wtf');

    $('button').click(function() {
        console.log('wtf');
    });

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