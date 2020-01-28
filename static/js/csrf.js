function getMeta(name) {
    // <meta name="foo" content="bar">
    // getMeta("foo") -=> "bar"
    
    const metas = document.getElementsByTagName("meta");

    for (let i = 0; i < metas.length; i++) {
	if (metas[i].getAttribute("name") === name) {
	    return metas[i].getAttribute("content");
	}
    }

  return "";
}

function addTokenToForms() {
    const forms = document.getElementsByTagName("form");

    for (let i = 0; i < forms.length; i++) {
	var input = document.createElement("input");
	input.type="hidden";
	input.name="csrf";
	input.value=getMeta("csrf");
	forms[i].appendChild(input);
    }
}
window.onload = addTokenToForms;
