form = document.getElementById("form");
if (form) {
  form.addEventListener("submit", function () {
    document.getElementById("loading").style.display = "block";
  });
}
