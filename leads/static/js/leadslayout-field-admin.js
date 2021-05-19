window.addEventListener("load", function() {
    (function($) {
        $('#id_layout_hr').on('change',function(){
            if($(this).is(':checked')){
                $('#id_layout_field').val('');
                $('#id_layout_field_display_only').prop('checked', false);
                $('#id_layout_nbsp').prop('checked', false);
            }
        });

        $('#id_layout_nbsp').on('change',function(){
            if($(this).is(':checked')){
                $('#id_layout_field').val('');
                $('#id_layout_field_display_only').prop('checked', false);
                $('#id_layout_hr').prop('checked', false);
            } 
        })

        $('#id_layout_field_display_only').on('change',function(){
            if($(this).is(':checked')){
                $('#id_layout_nbsp').prop('checked', false);
                $('#id_layout_hr').prop('checked', false);
            } 
        });

        $('#id_layout_field').on('change',function(){
            if($(this).val()!==''){
                $('#id_layout_nbsp').prop('checked', false);
                $('#id_layout_hr').prop('checked', false);
            }
        })
    })(django.jQuery);
});
