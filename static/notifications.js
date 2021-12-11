function postData(type) {
	console.log("type");
	$.post("",{request_type: (type == 1 ? "Accept" : "Reject")},() => window.location.reload());
}