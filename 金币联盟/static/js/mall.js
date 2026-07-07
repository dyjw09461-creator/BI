document.addEventListener("click", (event) => {
  const button = event.target.closest(".buy-row a,.buy-row button");
  if (!button) return;
  button.animate([{ transform: "scale(1)" }, { transform: "scale(1.08)" }, { transform: "scale(1)" }], {
    duration: 180,
    easing: "ease-out"
  });
});
