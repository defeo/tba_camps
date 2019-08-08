$(function() {
    // Show/hide dependent fields
    $('#id_caf').on('change', 'input:checked', function() {
	var $this = $(this);
	$('#id_cafno').trigger($this.val() == 'N'
				 ? 'hide.cafno'
				 : 'show.cafno');
    });
    $('#id_cafno')
	.on('show.cafno hide.cafno', function(e) {
	    $(this).prop('required', e.type == 'show');
	})
	.parent()
	.on('show.cafno hide.cafno', function(e, speed) {
	    $this = $(this);
	    $this[e.type]('slow');
	});
    $('#id_caf input:checked').trigger('change');
});
