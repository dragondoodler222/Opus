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
	//POST HERE
	modal.style.display = "none";
	window.location = '/';
}

function completeTask() {
	//POST HERE
	modal2.style.display = "none";
	window.location = '/';
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