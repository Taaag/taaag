(function ($) {
    'use strict';

    $(document).on('click', ".tag-cloud-tag:not(.tagged)", function () {
        insertNewTag($(this).text());
    });

    $(document).on('click', ".tag-cloud-tag.tagged", function () {
        $.bootstrapGrowl("You have already tagged " + $(this).text(), {align: 'center', 'type': 'warning'});
    });
}(jQuery));