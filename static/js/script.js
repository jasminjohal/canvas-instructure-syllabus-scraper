const form = document.getElementById("form");
if (form) {
  form.addEventListener("submit", function () {
    document.getElementById("loading").style.display = "block";
  });

  form.addEventListener("change", (event) => {
    document.getElementById("error").style.display = "none";
  });
}
