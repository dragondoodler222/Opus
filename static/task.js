var scrolled = false;
function updateScroll(){
    if(!scrolled){
        var element = document.getElementsByClassName("messages")[0];
        element.scrollTop = element.scrollHeight;
    }
}

setInterval(updateScroll,100);
var messel = document.getElementsByClassName("messages")[0];
$(".messages").on('scroll', function(){

    scrolled=true;
    if (messel.scrollTop == messel.scrollHeight- messel.clientHeight) {
     	scrolled = false;
    }
});




function postData(type) {
	$.post("",{request_type: type},() => window.location.reload());
}

document.getElementsByClassName("chatroomb4")[0].onclick = el => {
	document.getElementsByClassName("chatroom")[0].classList.toggle("closed");
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



	



let checker;

let task = document.getElementById("task_id");
let task_id = document.getElementById("task_id").value;
function get_messages() {
	console.log("JIMMY")
	$.getJSON('/get_messages/' + task_id, {
	     //Get a JSON formatted value from the route _get_words, which will allow flask in python to communicate with AJAX in JS
	}, function(data) {
		let msgDiv = document.getElementById("messages")
		console.log(data.result)
		let response = data.result;
		let messages = response.posts
		if (checker){
			let cleaned_messages = messages.filter(x => !checker.map(x => x['id']).includes(x['id']));
			let uid_to_username = response.uid_to_username;
			for (ind in cleaned_messages){
				let newMsg = document.createElement("div");
				let content = document.createElement("p");
				console.log(cleaned_messages[ind])
				console.log(uid_to_username[cleaned_messages[ind].author])
				content.innerHTML = uid_to_username[cleaned_messages[ind].author] + ": " + cleaned_messages[ind].message;
				newMsg.appendChild(content);
				msgDiv.appendChild(newMsg);
			}
			
		}else{
			let uid_to_username = response.uid_to_username;
			for (ind in messages){
				let newMsg = document.createElement("div");
				let content = document.createElement("p");
				console.log(messages[ind])
				console.log(uid_to_username[messages[ind].author])
				content.innerHTML = uid_to_username[messages[ind].author] + ": " + messages[ind].message;
				newMsg.appendChild(content);
				msgDiv.appendChild(newMsg);
			}
		}
		checker = messages
		console.log(checker, messages)
		console.log(checker==messages)
	});
	// if (r){
	// 	setTimeout(get_messages(true), 50000);
	// }
}
const interval = setInterval(function() {
	console.log("boboboboboobob")
    get_messages()
}, 5000);
get_messages();


// let task_id = document.getElementById("task_id").value;
// (function get_messages() {
	
//   $.get('/get_messages/'+task_id, function(data) {
//     // Now that we've completed the request schedule the next one.
//     let msgDiv = document.getElementById("messages")
// 	console.log(data.result)
// 	let response = data.result;
// 	let messages = response.posts
// 	checker = messages;
// 	let uid_to_username = response.uid_to_username;
// 	for (ind in messages){
// 		let newMsg = document.createElement("div");
// 		let content = document.createElement("p");
// 		console.log(messages[ind])
// 		console.log(uid_to_username[messages[ind].author])
// 		content.innerHTML = uid_to_username[messages[ind].author] + ": " + messages[ind].message;
// 		newMsg.appendChild(content);
// 		msgDiv.appendChild(newMsg);
// 	}
//     setTimeout(get_messages, 5000);
//   });
// })();

formEl = document.getElementById("txtbox")
$("#sendmsg").submit(function (e) {
	console.log("boboboboboobob")
	e.preventDefault();
	$.ajax({ 
	    url: '/createPost', 
	    type: 'POST', 
	    data: $('#sendmsg').serialize()
    });
    console.log(formEl)
    formEl.value = ""
    get_messages();
    get_messages();
}); 

