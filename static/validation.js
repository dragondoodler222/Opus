window.addEventListener('DOMContentLoaded',function(){
    let formEl = document.getElementById('taskform');
    formEl.addEventListener('submit', function(ev){
        
        let titleInput = document.getElementById('title');
        let descriptionInput = document.getElementById('description');
        let languagesInput = document.getElementById('languages');
        let hminInput = document.getElementById('hmin');
        let hmaxInput = document.getElementById('hmax');
        let cmaxInput = document.getElementById('cmax');
        let imageInput = document.getElementById('image');
        let container = document.getElementById("langtags");
        let spans = container.getElementsByTagName("span");
        let hiddenInput = document.getElementById("hiddenInput");
        
        rv = true;
        if (titleInput.value == "") {
            titleInput.classList.add('error');
            titleInput.parentNode.classList.add('error');
            rv = false;
        } else {
            /* clear error classes and let submit happen */
            titleInput.classList.remove('error');
            titleInput.parentNode.classList.remove('error');
        }
        if (spans.length == 0) {
            languagesInput.parentNode.parentNode.classList.add('error');
            languagesInput.parentNode.parentNode.parentNode.classList.add('error');
            rv = false;
        } else {
            /* clear error classes and let submit happen */
            languagesInput.parentNode.parentNode.classList.remove('error');
            languagesInput.parentNode.parentNode.parentNode.classList.remove('error');
        }
        if (hmaxInput.value == "") {
            hmaxInput.classList.add('error');
            hmaxInput.parentNode.classList.add('error');
            rv = false;
        } else {
            /* clear error classes and let submit happen */
            hmaxInput.classList.remove('error');
            hmaxInput.parentNode.classList.remove('error');
        }
        if (hminInput.value == "") {
            hminInput.classList.add('error');
            hminInput.parentNode.classList.add('error');
            rv = false;
        } else {
            /* clear error classes and let submit happen */
            hminInput.classList.remove('error');
            hminInput.parentNode.classList.remove('error');
        }
        if (cmaxInput.value == "") {
            cmaxInput.classList.add('error');
            cmaxInput.parentNode.classList.add('error');
            rv = false;
        } else {
            /* clear error classes and let submit happen */
            cmaxInput.classList.remove('error');
            cmaxInput.parentNode.classList.remove('error');
        }
        if (rv == false){
            ev.preventDefault();
        }
        hiddenInput.value = ""
        for (ind in spans){
            if (spans[ind].classList.contains("tag")){
              if (ind == 0){
                    hiddenInput.value += spans[ind].textContent.slice(0, -1)
                }else{
                    hiddenInput.value += ", " + spans[ind].textContent.slice(0, -1)
                }  
            }
            
           
        }

        hiddenInput.value += ", " + languagesInput.value;
    });
}); 