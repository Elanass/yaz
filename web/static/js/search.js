document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const cards = document.querySelectorAll(".card");

    searchInput.addEventListener("input", () => {
        const query = searchInput.value.toLowerCase();
        cards.forEach(card => {
            const content = card.textContent.toLowerCase();
            card.style.display = content.includes(query) ? "block" : "none";
        });
    });
});
