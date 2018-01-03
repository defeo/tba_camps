$('.uploads').each(function(i, u) {
    var $u = $(u);
    var b = $u.find('button');
    b.prop('disabled', true);

    $u.find('.fileinput').each(function(i, f) {
	var $f = $(f);
	var msg = $f.find('.uploading');
	var link = $f.find('a');
	$f.find('input').on('change', function(e) {
	    b.prop('disabled', false);
	    var name = e.target.value.split(/\\|\//);
	    name = name[name.length-1];
	    msg.text(name.substr(0,30) + (name.substr(30) && '…' || ''));
	    link.text('');
	});
    });
});
