(function ($) {
    'use strict';

    function insertNewTag(text) {
        var tags = $('#inputDescription').val() || [];
        if (tags.indexOf(text) == -1) {
            tags.push(text);
            $('#inputDescription').val(tags).trigger("change");
        }
    }

    $(document).on('click', ".tag-cloud-tag:not(.tagged)", function () {
        insertNewTag($(this).text());
    });

    $(document).on('click', ".tag-cloud-tag.tagged", function () {
        $.bootstrapGrowl("You have already tagged " + $(this).text(), {align: 'center', 'type': 'warning'});
    });

}(jQuery));