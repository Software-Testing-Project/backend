function handle_Change() {
  fetch("/people")
    .then((response) => response.text())
    .then((data) => {
      let change = document.getElementById("names");
      change.innerText = data;
    });
}
