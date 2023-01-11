$(document).ready(function() {
    console.log('loaded sphinx_hosting.js');
    $(".dropdown-toggle[data-bs-toggle='dropdown-ww']").click(function () {
        var target_id = $(this).attr('data-bs-target');
        var target = $(target_id);
        if ($(this).attr('aria-expanded') === 'false') {
            target.addClass('show');
            $(this).attr('aria-expanded', 'true');
        } else {
            $(this).attr('aria-expanded', 'true');
            target.removeClass('show');
        }
    })
});
