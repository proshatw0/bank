function addStartElement(){
    var startBackDiv = document.createElement("div");
    startBackDiv.classList.add("start_back");
    startBackDiv.id = "start_back";

    var startContenerDiv = document.createElement("div");
    startContenerDiv.classList.add("start-contener");
    startContenerDiv.id = "start-contener";

    var h1Element = document.createElement("h1");
    h1Element.classList.add("start_h1");
    h1Element.textContent = "RaccoonBank";

    var imgElement = document.createElement("img");
    imgElement.classList.add("start_logo");
    imgElement.src = "/static/images/logo.png";
    imgElement.alt = "logo";

    var h2Element = document.createElement("h2");
    h2Element.classList.add("start_h2");
    h2Element.textContent = "Надежные лапки";

    startContenerDiv.appendChild(h1Element);
    startContenerDiv.appendChild(imgElement);
    startContenerDiv.appendChild(h2Element);

    startBackDiv.appendChild(startContenerDiv);

    document.body.appendChild(startBackDiv);
}

function removeElement() {
    let referrer = document.referrer;

    if (!referrer || referrer.indexOf("127.0.0.1:8000") !== 7) {
        addStartElement()
        let element = document.getElementById("start_back");
        setTimeout(function() {
            element.style.transition = 'opacity 1s ease';
            element.style.opacity = 0;
            setTimeout(function() {
                element.remove();
            }, 1000); 
        }, 1000);
    }
}

window.onload = function() {
    removeElement();
};