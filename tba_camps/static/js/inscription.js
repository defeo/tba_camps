$(function() {
    // Show/hide dependent fields
    $('#id_formule').on('change', 'input:checked', function() {
	var $this = $(this);
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
	$('#id_mode').trigger($this.data('mode')
			      ? 'show.formule'
			      : 'hide.formule');
    });
    $('#id_accompagnateur, #id_train, #id_chambre, #id_navette_a, #id_navette_r, #id_mode').parent()
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

    // Complete formule/hebergement managemet
    $('#id_semaines').on('change', function() {
	// Function to disable options
	var shutdown = function ($label, cond, clas) {
	    $input = $label.find('input');
	    if (cond) $input.prop('checked', false);
	    $label.toggleClass(clas || 'complet', cond);
	    $input.prop('disabled', cond);
	    return cond;
	};
	
	var update = function(field, id) {
	    // Get complete options
	    var complet = [];
	    $('#id_semaines input:checked').each(function() {
		this.dataset[field + '_complet'].split(',').forEach(function(f) {
		    if (f && complet.indexOf(f) < 0)
			complet.push(f);
		});
	    });
	    console.log(complet);
	    
	    // Disable unavailable options
	    $(id + ' label').each(function() {
		var $this = $(this);
		var $input = $this.find('input');
		shutdown($this, complet.indexOf($input.val()) >= 0);
	    });
	}
	update('formule', '#id_formule');
	update('hbgt', '#id_hebergement');
    });
    
    // Trigger events if dependee fields are checked
    $('#id_formule input:checked, #id_semaines input:checked, #id_hebergement input:checked').trigger('change');
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
