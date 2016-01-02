$(function() {
    // Show/hide dependent fields
    $('#id_formule').on('change', 'input:checked', function() {
	var $this = $(this);
	$('#id_hebergement').trigger($this.data('hebergement')
				     ? 'show.formule'
				     : 'hide.formule');
	$('#id_chambre').trigger($this.data('chambre')
				 ? 'show.formule'
				 : 'hide.formule');
	$('#id_accompagnateur').trigger($this.data('accompagnateur')
					? 'show.formule'
					: 'hide.formule');
	$('#id_train').trigger($this.data('train')
			       ? 'show.formule'
			       : 'hide.formule');
	$('#id_navette_a, #id_navette_r').trigger($this.data('navette')
						  ? 'show.formule'
						  : 'hide.formule');
	$('#id_assurance').trigger($this.data('assurance')
			       ? 'show.formule'
			       : 'hide.formule');
	$('#id_mode').trigger($this.data('mode')
			      ? 'show.formule'
			      : 'hide.formule');
    });
    $('#id_hebergement, #id_accompagnateur, #id_train, #id_chambre, #id_navette_a, #id_navette_r, #id_assurance, #id_mode').parent()
	.hide()
	.on('show.formule hide.formule', function(e, speed) {
	    $(this)[e.type]('slow');
	});

    $('#id_licencie').on('change', 'input:checked', function() {
	$('#id_licence').trigger($(this).val() == 'O'
				 ? 'show.licence'
				 : 'hide.licence');
    });
    $('#id_licence').parent()
	.hide()
	.on('show.licence hide.licence', function(e, speed) {
	    $(this)[e.type]('slow');
	});

    // Update cost table
    $('#id_semaines, #id_formule, #id_train, #id_assurance, #id_navette_a, #id_navette_r, #id_mode')
	.on('change', function() {
	    var formule = $('#id_formule input:checked'),
		nsemaines = $('#id_semaines input:checked').length;
	    if (!formule.length) return;
	    var costs = {
		prix       : formule.data('prix') * nsemaines,
		cotisation : formule.data('cotisation'),
		taxe       : formule.data('taxe'),
		taxe_gym   : formule.data('taxe_gym') * nsemaines,
		assurance  : $('#id_assurance input:checked').val(),
		navette    : parseInt($('#id_navette_a input:checked').val()) 
		             + parseInt($('#id_navette_r input:checked').val()),
		train      : $('#id_train').val(),
	    }
	    
	    var total = 0, acompte = 0, sum = $('#cost-summary');
	    sum.find('.prix, .cotisation, .taxe, .taxe_gym, .assurance, .train, .navette')
		.each(function() {
		    var $this = $(this);
		    var clas = $this.attr('class');
		    var c = parseInt(costs[clas]);
		    if (c == 0
			|| (clas == 'train' && !formule.data('train'))
			|| (clas == 'navette' && !formule.data('navette'))
			|| (clas == 'assurance' && !formule.data('assurance'))) {
			$this.hide('fast');
		    } else {
			total += c;
			acompte += c * parseInt($this.data('acompte')) / 100;
			$this.show('fast').find('td:nth-child(2)').html(c);
		    }
		});
	    sum.find('.total td:nth-child(2)').html(total);
	    sum.find('.acompte td:nth-child(2)').html(Math.floor(acompte));
	});
    
    // Trigger events if dependee fields are checked
    $('#id_formule input:checked').trigger('change');
    $('#id_licencie input:checked').trigger('change');
});
