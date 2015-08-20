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
    $("#PleaseWaitChangePermissions").show();
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
                $("#PleaseWaitChangePermissions").hide();
            }
        }
    });
};

$('.btn_suspend_user').click(function(){
    $("#PleaseWaitSuspension").show();
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
                $("#PleaseWaitSuspension").hide();
                alert(message);
            }
        }
    });
});

$('.btn_activate_user').click(function(){
    $("#PleaseWaitSuspension").show();
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
                $("#PleaseWaitSuspension").hide();
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
    $("#PleaseWait").show();
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
                $("#PleaseWait").hide();
                alert(message);
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

$('.btn_delete_blocked_flag').click(function(){
    if (confirm('Do you really want to delete blocking flag of this user?'))
    {
        var blocker_id = $(this).parent().parent().data('blocker_id');
        var blocked_id = $(this).parent().parent().data('blocked_id');

        //console.log(blocker_id);
        //console.log(blocked_id);

        delete_blocked_flag(blocker_id, blocked_id, function(status, message){
            if (status != 0)
            {
                alert(message);
            }
        });
    }
});

delete_blocked_flag = function(blocker_id, blocked_id, completion)
{
    $.ajax({
        url: '/api/admin/users/blocked?' + $.param({'blocker_id': blocker_id}, true) + '&'
            + $.param({'blocked_id': blocked_id}, true),
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

// TODO THIS IS TEST

// TODO platforms
$('.btn_add_platform').click(function(){
    new_platform_title = document.getElementById("new_platform_title").value;
    new_platform_title_without_whitespaces = new_platform_title.split(' ').join('');
    if (!new_platform_title || !new_platform_title_without_whitespaces) {
        alert('Empty platform title')
    } else {
        $.ajax({
            url: '/api/admin/metatags/platforms',
            type: 'POST',
            data: {
                'new_platform_title': new_platform_title
            },
            success: function(data) {
                var status = data['status'];
                var message = data['message'];
                if (status == 0 ) {
                    location.reload();
                } else {
                    alert(message);
                }
            }
        });
    }
});

$('.btn_edit_platform').click(function(){
    platform_id = $(this).parent().parent().data('id');
    platform_title = $(this).parent().parent().data('title');
    platform_description = $(this).parent().parent().data('description');
    platform_image = $(this).parent().parent().data('image_url');
    $('#editing_platform_id').val(platform_id);
    $('#editing_platform_title').val(platform_title);
    if (platform_description) {
        $('#editing_platform_description').val(platform_description);
    }

    if (platform_image) {
        $('#editing_platform_image_href').attr('href', platform_image);
        $('#editing_platform_image').attr('src', platform_image);
        $('#editing_platform_image_url').val(platform_image);
    }
});

$('.btn_save_edited_platform').click(function(){
    platform_id = document.getElementById("editing_platform_id").value;
    platform_title = document.getElementById("editing_platform_title").value;
    $.ajax({
        url: '/api/admin/metatags/platforms',
        type: 'PUT',
        data: {
            'platform_id': platform_id,
            'platform_title': platform_title
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

$('.btn_delete_platform').click(function(){
    if (confirm('Do you really want to delete this platform and all its children?'))
    {
        platform_id = $(this).parent().parent().data('id');

        delete_platform(platform_id, function(status, message){
            if (status != 0)
            {
                alert(message);
            }
        });
    }
});

delete_platform = function(platform_id, completion)
{
    $.ajax({
        url: '/api/admin/metatags/platforms?' + $.param({'platform_id': platform_id}, true),
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

// TODO category

$('.btn_add_category').click(function(){
    new_category_title = document.getElementById("new_category_title").value;
    new_category_title_without_whitespaces = new_category_title.split(' ').join('');
    platform_id = $(this).parent().parent().find('#category_platform_select').val();
    if (!new_category_title || !new_category_title_without_whitespaces || platform_id == 0) {
        alert('Empty category title / platform name')
    } else {
        $.ajax({
            url: '/api/admin/metatags/categories',
            type: 'POST',
            data: {
                'new_category_title': new_category_title,
                'platform_id': platform_id
            },
            success: function(data) {
                var status = data['status'];
                var message = data['message'];
                if (status == 0 ) {
                    location.reload();
                } else {
                    alert(message);
                }
            }
        });
    }
});

$('.btn_edit_category').click(function(){
    category_id = $(this).parent().parent().data('id');
    category_title = $(this).parent().parent().data('title');
    platform_id = $(this).parent().parent().data('platform_id');
    $('#editing_category_id').val(category_id);
    $('#editing_category_title').val(category_title);
    document.getElementById('edit_category_select').value=platform_id;
});

$('.btn_save_edited_category').click(function(){
    category_id = document.getElementById("editing_category_id").value;
    category_title = document.getElementById("editing_category_title").value;
    platform_id = $(this).parent().parent().find('#edit_category_select').val();
    $.ajax({
        url: '/api/admin/metatags/categories',
        type: 'PUT',
        data: {
            'category_id': category_id,
            'category_title': category_title,
            'platform_id': platform_id
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

$('.btn_delete_category').click(function(){
    if (confirm('Do you really want to delete this category and all its children?'))
    {
        category_id = $(this).parent().parent().data('id');

        delete_category(category_id, function(status, message){
            if (status != 0)
            {
                alert(message);
            }
        });
    }
});

delete_category = function(category_id, completion)
{
    $.ajax({
        url: '/api/admin/metatags/categories?' + $.param({'category_id': category_id}, true),
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

// TODO subcategory
$('.btn_add_subcategory').click(function(){
    new_subcategory_title = document.getElementById("new_subcategory_title").value;
    new_subcategory_title_without_whitespaces = new_subcategory_title.split(' ').join('');
    category_id = $(this).parent().parent().find('#subcategory_category_select').val();
    if (!new_subcategory_title || !new_subcategory_title_without_whitespaces || category_id == 0) {
        alert('Empty subcategory title / category name')
    } else {
        $.ajax({
            url: '/api/admin/metatags/subcategories',
            type: 'POST',
            data: {
                'new_subcategory_title': new_subcategory_title,
                'category_id': category_id
            },
            success: function(data) {
                var status = data['status'];
                var message = data['message'];
                if (status == 0 ) {
                    location.reload();
                } else {
                    alert(message);
                }
            }
        });
    }
});

$('.btn_edit_subcategory').click(function(){
    subcategory_id = $(this).parent().parent().data('id');
    subcategory_title = $(this).parent().parent().data('title');
    category_id = $(this).parent().parent().data('category_id');

    $('#editing_subcategory_id').val(subcategory_id);
    $('#editing_subcategory_title').val(subcategory_title);
    document.getElementById('edit_subcategory_select').value=category_id;
});

$('.btn_save_edited_subcategory').click(function(){
    subcategory_id = document.getElementById("editing_subcategory_id").value;
    subcategory_title = document.getElementById("editing_subcategory_title").value;
    category_id = $(this).parent().parent().find('#edit_subcategory_select').val();
    $.ajax({
        url: '/api/admin/metatags/subcategories',
        type: 'PUT',
        data: {
            'category_id': category_id,
            'subcategory_id': subcategory_id,
            'subcategory_title': subcategory_title
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

$('.btn_delete_subcategory').click(function(){
    if (confirm('Do you really want to delete this subcategory and all its children?'))
    {
        subcategory_id = $(this).parent().parent().data('id');

        delete_subcategory(subcategory_id, function(status, message){
            if (status != 0)
            {
                alert(message);
            }
        });
    }
});

delete_subcategory = function(category_id, completion)
{
    $.ajax({
        url: '/api/admin/metatags/subcategories?' + $.param({'subcategory_id': subcategory_id}, true),
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

// TODO colour

$('.btn_add_colour').click(function(){
    new_colour_title = document.getElementById("new_colour_title").value;
    new_colour_title_without_whitespaces = new_colour_title.split(' ').join('');
    subcategory_id = $(this).parent().parent().find('#colour_subcategory_select').val();
    new_colour_code = document.getElementById("color_pickier").value;
    disable_colour = document.getElementById('color_pickier_checkbox').checked;
    if (!new_colour_title || !new_colour_title_without_whitespaces || subcategory_id == 0) {
        alert('Empty subcategory title / colour name')
    } else {
        $.ajax({
            url: '/api/admin/metatags/colours',
            type: 'POST',
            data: {
                'new_colour_title': new_colour_title,
                'subcategory_id': subcategory_id,
                'new_colour_code': new_colour_code,
                'disable_colour': disable_colour
            },
            success: function(data) {
                var status = data['status'];
                var message = data['message'];
                if (status == 0 ) {
                    location.reload();
                } else {
                    alert(message);
                }
            }
        });
    }
});

$('.btn_edit_colour').click(function(){
    colour_id = $(this).parent().parent().data('id');
    colour_title = $(this).parent().parent().data('title');
    colour_code = $(this).parent().parent().data('code');
    subcategory_id = $(this).parent().parent().data('subcategory_id');

    $('#editing_colour_id').val(colour_id);
    $('#editing_colour_title').val(colour_title);
    document.getElementById('edit_colour_select').value=subcategory_id;
    if (colour_code == '') {
        document.getElementById('edit_color_pickier_checkbox').click();
    } else {
        $('#edit_color_pickier').val(colour_code);
        $('#edit_color_pickier').css('background', '#' + colour_code);
        if (colour_code == '000000') {
            $('#edit_color_pickier').css('color', '#FFFFFF');
        }

    }
});

$('.btn_save_edited_colour').click(function(){
    colour_id = document.getElementById("editing_colour_id").value;
    colour_title = document.getElementById("editing_colour_title").value;
    subcategory_id = $(this).parent().parent().find('#edit_colour_select').val();
    colour_code = document.getElementById("edit_color_pickier").value;
    disable_colour = document.getElementById('edit_color_pickier_checkbox').checked;
    $.ajax({
        url: '/api/admin/metatags/colours',
        type: 'PUT',
        data: {
            'colour_id': colour_id,
            'colour_title': colour_title,
            'colour_code': colour_code,
            'disable_colour': disable_colour,
            'subcategory_id': subcategory_id
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

$('.btn_delete_colour').click(function(){
    if (confirm('Do you really want to delete this colour?'))
    {
        colour_id = $(this).parent().parent().data('id');

        delete_colour(colour_id, function(status, message){
            if (status != 0)
            {
                alert(message);
            }
        });
    }
});

delete_colour = function(colour_id, completion)
{
    $.ajax({
        url: '/api/admin/metatags/colours?' + $.param({'colour_id': colour_id}, true),
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

// TODO conditon

$('.btn_add_condition').click(function(){
    new_condition_title = document.getElementById("new_condition_title").value;
    new_condition_title_without_whitespaces = new_condition_title.split(' ').join('');
    subcategory_id = $(this).parent().parent().find('#condition_subcategory_select').val();
    if (!new_condition_title || !new_condition_title_without_whitespaces || subcategory_id == 0) {
        alert('Empty subcategory title / condition name')
    } else {
        $.ajax({
            url: '/api/admin/metatags/conditions',
            type: 'POST',
            data: {
                'new_condition_title': new_condition_title,
                'subcategory_id': subcategory_id
            },
            success: function(data) {
                var status = data['status'];
                var message = data['message'];
                if (status == 0 ) {
                    location.reload();
                } else {
                    alert(message);
                }
            }
        });
    }
});


$('.btn_edit_condition').click(function(){
    condition_id = $(this).parent().parent().data('id');
    condition_title = $(this).parent().parent().data('title');
    subcategory_id = $(this).parent().parent().data('subcategory_id');

    $('#editing_condition_id').val(condition_id);
    $('#editing_condition_title').val(condition_title);
    document.getElementById('edit_condition_select').value=subcategory_id;
});

$('.btn_save_edited_condition').click(function(){
    condition_id = document.getElementById("editing_condition_id").value;
    condition_title = document.getElementById("editing_condition_title").value;
    subcategory_id = $(this).parent().parent().find('#edit_condition_select').val();
    $.ajax({
        url: '/api/admin/metatags/conditions',
        type: 'PUT',
        data: {
            'condition_id': condition_id,
            'condition_title': condition_title,
            'subcategory_id': subcategory_id
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

$('.btn_delete_condition').click(function(){
    if (confirm('Do you really want to delete this condition?'))
    {
        condition_id = $(this).parent().parent().data('id');

        delete_condition(condition_id, function(status, message){
            if (status != 0)
            {
                alert(message);
            }
        });
    }
});

delete_condition = function(colour_id, completion)
{
    $.ajax({
        url: '/api/admin/metatags/conditions?' + $.param({'condition_id': condition_id}, true),
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

// listings
$('.btn_delete_listing').click(function(){
    if (confirm('Do you really want to delete this listing?'))
    {
        listing_id = $(this).parent().parent().data('id');

        delete_listing(listing_id, function(status, message){
            if (status != 0)
            {
                alert(message);
            }
        });
    }
});

delete_listing = function(listing_id, completion)
{
    $.ajax({
        url: '/api/admin/listings?' + $.param({'listing_id': listing_id}, true),
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

// ORDERS
$('.btn_order_investigating').click(function(){
    id = $(this).parent().parent().data('id');
    $.ajax({
        url: '/api/admin/listings/issues/new',
        type: 'PUT',
        data: {
            'id': id,
            'action': 1
        },
        success: function(data) {
            var status = data['status'];
            var message = data['message'];
            if (status == 0 ) {
                location.replace("investigating");
            } else {
                alert(message);
            }
        }
    });
});

$('.btn_order_canceled').click(function(){
    id = $(this).parent().parent().data('id');
    $.ajax({
        url: '/api/admin/listings/issues/investigating',
        type: 'PUT',
        data: {
            'id': id,
            'action': 2
        },
        success: function(data) {
            var status = data['status'];
            var message = data['message'];
            if (status == 0 ) {
                location.replace("canceled");
            } else {
                alert(message);
            }
        }
    });
});

$('.btn_order_resolved').click(function(){
    id = $(this).parent().parent().data('id');
    $.ajax({
        url: '/api/admin/listings/issues/investigating',
        type: 'PUT',
        data: {
            'id': id,
            'action': 4
        },
        success: function(data) {
            var status = data['status'];
            var message = data['message'];
            if (status == 0 ) {
                location.replace("resolved");
            } else {
                alert(message);
            }
        }
    });
});

$(".clickable-row").click(function() {
    window.open($(this).data("href"), '_blank').focus();
    //win = window.open($(this).data("href"), '_blank');
    //win.focus();
});