$(function() {
    $('#id_assurance').on('change', function() {
        $('#id_assurance_confirm').trigger('change.assurance');
    });
    
    $('#id_assurance_confirm').on('change.assurance', function() {
        var $this = $(this);
        var val = $('#id_assurance input:checked').val() !== '0.00';
        $this.prop('disabled', val);
        $this.prop('required', !val);
        $this.parent()[val ? 'hide' : 'show']('slow');
    }).parent().hide();
    
    $('#id_assurance_confirm').trigger('change.assurance');    

    $('[data-toggle="popover"]').popover();
});
