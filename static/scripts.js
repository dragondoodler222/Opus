function showUserDropdown() {
  document.getElementById("user-information-dropdown-content").classList.toggle("show");
}
window.onclick = function(event) {
  if (!event.target.matches('#user-information-dropdown')) {
	Array.from(document.getElementsByClassName("user-information-dropdown-content")).forEach(el => el.classList.remove('show'));
  }
}