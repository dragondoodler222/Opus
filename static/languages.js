//https://codepen.io/barman47/pen/gOwypmj
const langInput = document.querySelector("#languages");
const form = document.querySelector("#taskform");

const langContainer = document.querySelector(".language-container");
const langs = [];

const createTag = (tagValue) => {
    const value = tagValue.trim();

    if (value === "" || langs.includes(value)) return;

    const tag = document.createElement("span");
    const tagContent = document.createTextNode(value);
    tag.setAttribute('class', 'tag');
    tag.appendChild(tagContent);

    const close = document.createElement('span');
    close.setAttribute('class', 'remove-tag');
    close.innerHTML = '&#10006;'
    close.onclick = handleRemoveTag;

    tag.appendChild(close);
    langContainer.appendChild(tag);
    langs.push(tag);
    langInput.value = '';
    langInput.focus();
};

const handleRemoveTag = (e) => {
    const item = e.target.textContent;
    e.target.parentElement.remove();
    langs.splice(langs.indexOf(item), 1);
};

const handleFormSubmit = (e) => {
    e.preventDefault();
    createTag(langInput.value);
};

langInput.addEventListener('keyup', (e) => {
    const { key } = e;
    if (key === ','){
        createTag(langInput.value.substring(0,langInput.value.length-1));
    }
});

//form.addEventListener('submit', handleFormSubmit);