// Click any gallery image to open it full size. Escape or a click closes it.
(function () {
  var box = document.createElement("div");
  box.id = "lightbox";
  box.innerHTML = '<button type="button" aria-label="Close">&times;</button><img alt="">';
  document.body.appendChild(box);

  var full = box.querySelector("img");

  function close() {
    box.classList.remove("open");
    full.src = "";
  }

  document.addEventListener("click", function (ev) {
    var img = ev.target.closest("[data-lightbox] img");
    if (img) {
      full.src = img.dataset.full || img.currentSrc || img.src;
      box.classList.add("open");
      return;
    }
    if (ev.target.closest("#lightbox")) close();
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") close();
  });
})();
