function postData(type, id, username, index) {
	$.post("",{request_type: (type == 1 ? "Accept" : "Reject"), identifier: id, user: username, i: index},() => window.location.reload());
}