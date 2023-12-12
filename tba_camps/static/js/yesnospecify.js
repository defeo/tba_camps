$('.yns_radio')
    .on('change', function(e) {
	var yes = $(this).find(':checked').hasClass('yns_yes');
	$(this).parent().find('> input')
	    .prop('required', yes)
	    .prop('disabled', !yes)
	    .val(function(i, val) {
		return yes ? val : '';
	    });
    })
    .trigger('change');
