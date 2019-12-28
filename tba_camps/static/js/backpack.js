$('#backpacks button.toggle').on('click', function(e) {
    var form = $(this).parent().parent();
    form.toggleClass('active inactive');
    if (form.hasClass('inactive')) {
	form.find('input').each(function(n, i) {
	    i.value = i.getAttribute('value');
	});
    } else {
	form.find('.prenom input').focus();
    }
});
