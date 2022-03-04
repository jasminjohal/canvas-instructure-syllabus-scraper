const form = document.getElementById("form");

if (form) {
  form.addEventListener("submit", function () {
    document.getElementById("loading").style.display = "block";
  });

  form.addEventListener("change", (event) => {
    const errorMsgs = document.getElementsByClassName("error");
    for (let i = 0; i < errorMsgs.length; i++) {
      if (errorMsgs[i]) {
        errorMsgs[i].style.display = "none";
      }
    }
  });
}
