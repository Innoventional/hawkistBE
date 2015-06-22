/**
 * Created by ne_luboff on 22.06.15.
 */

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

    console.log(id);
    console.log(name);
    console.log(parent_tag_id);

        //$('#url_id').val(id);
        //$('#current_url').val(url);
    });