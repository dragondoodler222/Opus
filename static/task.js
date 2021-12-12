function postData(type) {
	$.post("",{request_type: type},() => window.location.reload());
}



var modal = document.getElementById("project-modal");
var span = document.getElementsByClassName("close")[0];

modal.addEventListener('mousedown', function(e){ e.preventDefault(); }, false);
var modalIndex = 0;
var modalImages = []
// When the user clicks on the button, open the modal 
openDeleteConfirmModal = () => {
	modal.style.display = "flex";
};

function deleteTask() {
	$.post("",{request_type: "delete"},() => window.location = '/');
	modal.style.display = "none";
}

function completeTask() {
	//POST HERE
	$.post("",{request_type: "complete"},() => window.location = '/');

	modal2.style.display = "none";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
	modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
document.getElementsByClassName("modal")[0].onclick = function(event) {
	modal.style.display = "none";
}

var modal2 = document.getElementById("project-modal2");
var span2 = document.getElementsByClassName("close2")[0];

modal2.addEventListener('mousedown', function(e){ e.preventDefault(); }, false);
openCompleteConfirmModal = () => modal2.style.display = "flex";

span2.onclick = function() {
	modal2.style.display = "none";
}

document.getElementsByClassName("modal2")[0].onclick = function(event) {
	modal2.style.display = "none";
}


let task = document.getElementById("task_id");
	let task_id = document.getElementById("task_id").value;
	let response = $.getJSON('/get_messages/' + task_id, {
	     //Get a JSON formatted value from the route _get_words, which will allow flask in python to communicate with AJAX in JS
	}, function(data) {
		let msgDiv = document.getElementById("chatroom")
		console.log(data.result)
		let response = data.result;
		for (ind in response){
			let newMsg = document.createElementByTag("div");
			let content = document.createElementByTag("p")
			console.log(response[ind])
		}
	});

	


$(document).ready(function () {

	$("#sendmsg").submit(function (e) {
		e.preventDefault();
		let response = $.ajax({ 
		    url: '/createPost', 
		    type: 'POST', 
		    data: $('#sendmsg').serialize()
	    });
	    console.log(response)
	}); 
});

