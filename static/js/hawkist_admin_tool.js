/**
 * Created by ne_luboff on 22.06.15.
 */


$(document).ready(function () {
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.scrollup').fadeIn();
        } else {
            $('.scrollup').fadeOut();
        }
    });

    $('.scrollup').click(function () {
        $("html, body").animate({
            scrollTop: 0
        }, 600);
        return false;
    });

});

//tags tab functionality

$('.btn_add_tag').click(function(){
    var parent_tag_id = $(this).parent().parent().find('#add_tag_select').val();
    var new_tag_name = document.getElementById("new_tag_name").value;
    add_tag(parent_tag_id, new_tag_name)
});

add_tag = function(parent_tag_id, new_tag_name){
    $.ajax({
        url: '/api/admin/tags',
        type: 'POST',
        data: {
            'parent_tag_id': parent_tag_id,
            'new_tag_name': new_tag_name
        },
        success: function(data) {
            var status = data['status'];
            var message = data['message'];
            if (status == 0 )
            {
                location.reload();
            }else
            {
                alert(message);
            }
        }
    });
};


$('.btn_edit_tag').click(function(){
    var id = $(this).parent().parent().data('id');
    var name = $(this).parent().parent().data('name');
    var parent_tag_id = $(this).parent().parent().data('parent_tag_id');

    $('#editing_tag_id').val(id);
    $('#editing_tag_name').val(name);

    if (typeof parent_tag_id == 'number') {
        $(".edit_tag_parent_tag select").val(parent_tag_id);
    }
});

$('.btn_save_edited_tag').click(function(){
    var editing_parent_tag_id = $(this).parent().parent().find('#edit_tag_select').val();
    var editing_tag_name = document.getElementById("editing_tag_name").value;
    var editing_tag_id = document.getElementById("editing_tag_id").value;

    save_edited_tag(editing_tag_id, editing_tag_name, editing_parent_tag_id)
});

save_edited_tag = function(editing_tag_id, editing_tag_name, editing_parent_tag_id){
    $.ajax({
        url: '/api/admin/tags',
        type: 'PUT',
        data: {
            'tag_id': editing_tag_id,
            'tag_name': editing_tag_name,
            'parent_tag_id': editing_parent_tag_id
        },
        success: function(data) {
            var status = data['status'];
            var message = data['message'];
            if (status == 0 )
            {
                location.reload();
            }else
            {
                alert(message);
            }
        }
    });
};

$('.btn_delete_tag').click(function(){
    if (confirm('Do you really want to delete this tag and all children tags?'))
    {
        var id = $(this).parent().parent().data('id');

        delete_tag(id, function(status, message){
            if (status != 0)
            {
                alert(message);
            }
        });
    }
});

delete_tag = function(tag_id, completion)
{
    $.ajax({
        url: '/api/admin/tags?' + $.param({'tag_id': tag_id}, true),
        type: 'DELETE',
        success: function(data) {
            var status = data['status'];
            var message = data['message'];
            completion(status, message);
            location.reload();
        }
    });
    return false;
};
