(function($) {
  'use strict';

  var myTagUrl = "https://taaag.sshz.org/api";

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

}(jQuery));