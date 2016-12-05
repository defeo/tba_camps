$(function() {
    // Show/hide dependent fields
    $('#id_formule').on('change', 'input:checked', function() {
	var $this = $(this);
	$('#id_hebergement').trigger(this.dataset.hebergements
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
	$('#id_licence, #id_club').trigger($(this).val() == 'O'
					   ? 'show.licence'
					   : 'hide.licence');
    });
    $('#id_licence, #id_club').parent()
	.hide()
	.on('show.licence hide.licence', function(e, speed) {
	    $(this)[e.type]('slow');
	});

    // Hebergement managemet
    $('#id_semaines, #id_formule').on('change', function() {
	// Get complet accomodations
	var complet = [];
	$('#id_semaines input:checked').each(function() {
	    this.dataset.complet.split(',').forEach(function(h) {
		if (h && complet.indexOf(h) < 0)
		    complet.push(h);
	    });
	});
	var applicable = String($('#id_formule input:checked').data('hebergements'));
	applicable = applicable ? applicable.split(',') : [];
	
	// Function to disable options
	var shutdown = function ($label, cond, clas) {
	    $input = $label.find('input');
	    if (cond) $input.prop('checked', false);
	    $label.toggleClass(clas || 'complet', cond);
	    $input.prop('disabled', cond);
	    return cond;
	};
	// Disable complete accomodations
	$('#id_hebergement label').each(function () {
	    var $this = $(this);
	    var $input = $this.find('input');
	    shutdown($this, applicable.indexOf($input.val()) < 0, 'hidden');
	    shutdown($this, complet.indexOf($input.val()) >= 0);
	});
	// Disable unavailable formules
	// Select accomodation if unique
	$('#id_formule label').each(function() {
	    var $this = $(this);
	    var $input = $(this).find('input');
	    var h = String($input.data('hebergements'));
	    if (h) {
		var open = h.split(',').reduce(function(a,b) {
		    return a.concat(complet.indexOf(b) >= 0 ? [] : [b]);
		}, []);
		
		shutdown($this, open.length == 0);
		
		if (open.length == 1 && $input.is(':checked')) {
		    $('#id_hebergement input[value=' + open[0] + ']').prop('checked', true);
		}
	    }
	});
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
    $('#id_formule input:checked, #id_semaines input:checked').trigger('change');
    $('#id_licencie input:checked').trigger('change');

    // Async fetch license no from ffbb.com
    $('#id_nom, #id_prenom, #id_naissance, #id_sexe, #id_sexe').on('change', function() {
	data = {
	    nom        : $('#id_nom').val() || null,
	    prenom     : $('#id_prenom').val() || null,
	    sexe       : {H:'M',F:'F'}[$('#id_sexe_0:checked, #id_sexe_1:checked').val()] || null,
	    naissance  : $('#id_naissance').val() || null,
	}
	if (data.nom && data.prenom && data.sexe)
	$.get('/api/ffbb/', data, function (data) {
	    if (data.licenses.length == 1) {
		lic = data.licenses[0]
		$lic = $('#id_licence')
		if (!$lic.val())
		    $lic.val(lic.numNational)
		$club = $('#id_club')
		if (!$club.val())
		    $club.val(lic.nomOrganisme)
	    }
	})
    });
});
