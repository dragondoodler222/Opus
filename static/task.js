function postData(type) {
	$.post("",{request_type: type},() => window.location.reload());
}



var modal = document.getElementById("project-modal");
var span = document.getElementsByClassName("close")[0];

modal.addEventListener('mousedown', function(e){ e.preventDefault(); }, false);
var modalIndex = 0;
var modalImages = []
// When the user clicks on the button, open the modal 
openConfirmModal = () => {
	modal.style.display = "flex";
};

function deleteTask() {
	console.log("hi");
	modal.style.display = "none";
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

