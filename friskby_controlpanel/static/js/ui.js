window.addEventListener("load", function () {

    var flashes = document.querySelectorAll(".flashes li");
    for (var i = 0; i < flashes.length; i++) {
        flashes[i].addEventListener("click", function (e) {
            var n = e.target;
            while (n.nodeName.toLowerCase() != "li") {
                n = e.target.parentNode;
            }
            n.classList.add("dismissed");
        })
    }

});
