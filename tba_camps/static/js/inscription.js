$(function() {
    // Show/hide dependent fields
    $('#id_formule').on('change', 'input:checked', function() {
	var $this = $(this)
	$('#id_hebergement').trigger($this.data('hebergement')
				     ? 'show.formule'
				     : 'hide.formule');
	$('#id_train').trigger($this.data('train')
			       ? 'show.formule'
			       : 'hide.formule');
    });
    $('#id_hebergement, #id_train').parent()
	.hide()
	.on('show.formule hide.formule', function(e, speed) {
	    $(this)[e.type]('slow');
	});

    // Update cost table
    $('#id_formule, #id_train, #id_assurance').on('change', function() {
	var formule = $('#id_formule input:checked');
	if (!formule.length) return;
	var costs = {
	    prix       : formule.data('prix'),
	    cotisation : formule.data('cotisation'),
	    taxe       : formule.data('taxe'),
	    assurance  : $('#id_assurance input:checked').val(),
	    train      : $('#id_train').val(),
	}

	var total = 0, sum = $('#cost-summary');
	sum.find('.prix, .cotisation, .taxe, .assurance, .train')
	    .each(function() {
		var $this = $(this);
		var clas = $this.attr('class')
		var c = parseInt(costs[clas]);
		if (c == 0 || (clas == 'train' && !formule.data('train'))) {
		    $this.hide('fast');
		} else {
		    total += c;
		    $this.show('fast').find('td:nth-child(2)').html(c);
		}
	    });
	sum.find('.total td:nth-child(2)').html(total);
	sum.find('.acompte td:nth-child(2)').html(Math.floor(total / 2));
    });

    // Trigger events if a Formule is checked
    $('#id_formule input:checked').trigger('change');
});
