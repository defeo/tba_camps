function bp_activate(form) {
    form.addClass('active');
    form.first('input').focus();
}
function bp_deactivate(form) {
    form.removeClass('active');
    // Restore field values
    form.find('input').each(function(n, i) {
	i.value = i.getAttribute('value');
    });
    form.find('select').each(function(n, i) {
	i.value = $(i).find('option[selected]').attr('value');
    });
}

$('#backpacks .bp-swag')
    .on('click', '.bp-create', function(e) {
	bp_activate($(e.delegateTarget).find('form.empty'));
    });
$('#backpacks form')
    .on('click', '.bp-modify', function(e) {
	bp_activate($(e.delegateTarget));
    })
    .on('click', '.bp-cancel', function(e) {
	bp_deactivate($(e.delegateTarget));
    });
