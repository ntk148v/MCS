$(function() {

    /* Functions */

    var loadForm = function() {
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function() {
                $("#modal-file").modal("show");
            },
            success: function(data) {
                $("#modal-file .modal-content").html(data.html_form);
            }
        });
    };

    var saveForm = function() {
        var form = $(this);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: form.attr("method"),
            dataType: 'json',
            success: function(data) {
                if (data.form_is_valid) {
                    // $("#book-table tbody").html(data.html_book_list);
                    $("#modal-file").modal("hide");
                } else {
                    $("#modal-file .modal-content").html(data.html_form);
                }
            }
        });
        return false;
    };


    /* Binding */

    // Create/Upload
    $(".js-file-upload").click(loadForm);
    $("#modal").on("submit", ".js-file-upload-form", saveForm);

    // Create folder
    $(".js-folder-create").click(loadForm);
    $("#modal").on("submit", ".js-folder-create-form", saveForm);

    // // Update
    // $("#book-table").on("click", ".js-update", loadForm);
    // $("#modal").on("submit", ".js-update-form", saveForm);

    // // Delete
    // $("#book-table").on("click", ".js-delete", loadForm);
    // $("#modal").on("submit", ".js-delete-form", saveForm);

});