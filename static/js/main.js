// main.js - animations globales
document.addEventListener("DOMContentLoaded", function() {
  // Fade-in sur les cartes
  const cards = document.querySelectorAll(".card");
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.classList.add("fade-in");
    }, index * 150);
  });

  // Bouton scroll-up
  const scrollBtn = document.getElementById("scrollUp");
  if (scrollBtn) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 200) scrollBtn.classList.add("show");
      else scrollBtn.classList.remove("show");
    });
  }

  // Autres animations globales à ajouter ici
});
