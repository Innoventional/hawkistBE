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

//for modal windows reload
$('.btn_reload').click(function(){
        location.reload();
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

//user tab
$('.btn_change_user_type').click(function(){
    user_id = $(this).parent().parent().data('id');
    user_type = $(this).parent().parent().data('user_type');
    $('input[name=user_type][value=' + user_type +']').attr('checked', true);
    $('#changing_user_id').val(user_id);
});


$('.btn_save_usertype').click(function(){
    user_id = document.getElementById("changing_user_id").value;
    user_type_id = $('input[name=user_type]:checked').val();
    change_user_type(user_id, user_type_id);
});

change_user_type = function(user_id, user_type_id){
    $.ajax({
        url: '/api/admin/users',
        type: 'POST',
        data: {
            'user_id': user_id,
            'user_type_id': user_type_id
        },
        success: function(data) {
            var status = data['status'];
            var message = data['message'];
            if (status == 0 )
            {
                $("#close_modal").click();
                alert(message);
                location.reload();
            }else
            {
                alert(message);
                location.reload();
            }
        }
    });
};

$('.btn_suspend_user').click(function(){
    user_id = $(this).parent().parent().data('id');
    $.ajax({
        url: '/api/admin/users',
        type: 'PUT',
        data: {
            'user_id': user_id,
            'action': 'suspend'
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
});

$('.btn_activate_user').click(function(){
    user_id = $(this).parent().parent().data('id');
    $.ajax({
        url: '/api/admin/users',
        type: 'PUT',
        data: {
            'user_id': user_id,
            'action': 'unsuspend'
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
});

$('.btn_edit_user').click(function(){
    //alert('Editing in future');
    user_id = $(this).parent().parent().data('id');
    username = $(this).parent().parent().data('username');
    email = $(this).parent().parent().data('email');
    phone = $(this).parent().parent().data('phone');
    $('#editing_user_id').val(user_id);
    $('#editing_username').val(username);
    $('#editing_email').val(email);
    $('#editing_phone').val(phone);
});

$('.btn_save_editing_user').click(function(){
    user_id = document.getElementById("editing_user_id").value;
    username = document.getElementById("editing_username").value;
    email = document.getElementById("editing_email").value;
    phone = document.getElementById("editing_phone").value;
    change_user_info(user_id, username, email, phone);
});

change_user_info = function(user_id, username, email, phone){
    $.ajax({
        url: '/api/admin/users',
        type: 'PUT',
        data: {
            'action': 'edit',
            'user_id': user_id,
            'username': username,
            'email': email,
            'phone': phone
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
                location.reload();
            }
        }
    });
};


$('.btn_delete_user').click(function(){
    if (confirm('Do you really want to delete this user?'))
    {
        var id = $(this).parent().parent().data('id');

        delete_user(id, function(status, message){
            if (status != 0)
            {
                alert(message);
            }
        });
    }
});

delete_user = function(user_id, completion)
{
    $.ajax({
        url: '/api/admin/users?' + $.param({'user_id': user_id}, true),
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