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
	$('#assurance').trigger($this.data('assurance')
				? 'show.formule'
				: 'hide.formule');
	$('#note_cotisation').trigger($this.data('cotisation') != '0.00'
				      ? 'show.formule'
				      : 'hide.formule',
				      $this.data('cotisation'));
	$('#note_taxe_gym').trigger($this.data('taxe_gym') != '0.00'
				    ? 'show.formule'
				    : 'hide.formule',
				    $this.data('taxe_gym'));
	$('#note_menage').trigger($this.data('taxe') != '0.00'
				  ? 'show.formule'
				  : 'hide.formule',
				  $this.data('taxe'));
    });
    $('#id_accompagnateur, #id_train, #id_chambre, #id_navette_a, #id_navette_r').parent()
	.add('#assurance, #note_cotisation, #note_taxe_gym, #note_menage')
	.hide()
	.on('show.formule hide.formule', function(e, amount) {
	    $this = $(this);
	    $this[e.type]('slow');
	    if (amount) {
		$this.find('.amount').text(amount.replace(/.00$/, ''));
	    }
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

    $('#id_assurance').on('change', function() {
        $('#id_assurance_confirm').trigger('change.assurance');
    });
    $('#id_assurance_confirm').on('change.assurance', function(e) {
        var $this = $(this);
        var val = $('#id_assurance input:checked').val() !== '0.00';
        $this.prop('disabled', val);
        //$this.prop('required', !val);
        $this.parent()[val ? 'hide' : 'show']('slow');
    }).parent().hide();

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
    // Always trigger assurance
    $('#id_assurance_confirm').trigger('change.assurance');    

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

    // Reversible show/hide table
    $('[for="id_reversible"]').on('click', function(e) {
	$(this).find('table').toggleClass('active');
	return false;
    });
    $('body').on('click', function() {
	$('[for="id_reversible"] table').removeClass('active');
    });

    // Reversible auto-select
    $('#id_taille').on('keyup', function() {
	var rev = $('#id_reversible');
	var t = parseInt(this.value);
	rev.find('option').filter(function(i, o) {
	    return parseInt(o.dataset.min) <= t && t <= parseInt(o.dataset.max);
	}).attr('selected', true);
    });
    $('#id_reversible').on('change', function() {
	var $this = $(this);
	var t = parseInt($('#id_taille').val());
	var o = $this.parent().find(':selected');
	if (parseInt(o.data('min')) > t || t > parseInt(o.data('max'))) {
	    $this.parent().addClass('taille-mismatch');
	} else {
	    $this.parent().removeClass('taille-mismatch');
	}
    });
});
