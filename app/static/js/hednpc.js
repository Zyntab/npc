function cancel_delete(charname) {
	var url = "{{ url_for('character', charname=" + charname + ") }}";
	window.location = url;
}

function confirm_delete(delname) {
	var url = "{{ url_for('del_char', delname=" + charname + ") }}";
	window.location = url;
}
