function postData(type) {
	$.post("",{request_type: type},() => window.location.reload());
}