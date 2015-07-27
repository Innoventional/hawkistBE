/**
 * Created by ne_luboff on 27.07.15.
 */
$('#add_platform_form').ajaxForm({
        url : $(this).attr('action'),
        dataType : 'json',
        success: function(data) {
            var status = data['status'];
            var message = data['message'];
            if (status == 0 )
            {
                location.replace('/api/admin/metatags/platforms');
            } else
            {
                alert(message);
            }
        }
});

$('#edit_platform_form').ajaxForm({
        url : $(this).attr('action'),
        dataType : 'json',
        success: function(data) {
            var status = data['status'];
            var message = data['message'];
            if (status == 0 )
            {
                location.replace('/api/admin/metatags/platforms');
            } else
            {
                alert(message);
            }
        }
});