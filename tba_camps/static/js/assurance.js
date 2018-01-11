$(function() {
    $('#id_assurance').on('change', function() {
	$('#id_assurance_confirm').trigger('change.assurance');
    });
    
    $('#id_assurance_confirm').on('change.assurance', function() {
	var $this = $(this);
	var val = $('#id_assurance input:checked').val() === 'True';
	$this.prop('disabled', val);
	$this.prop('required', !val);
	$this.parent()[val ? 'hide' : 'show']('slow');
    });
    
    $('#id_assurance_confirm').trigger('change.assurance');    
});
