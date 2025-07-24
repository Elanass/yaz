document.addEventListener("DOMContentLoaded", () => {
    const resultsContainer = document.getElementById("results-container");

    function renderResults(data) {
        resultsContainer.innerHTML = ""; // Clear existing content

        const confidenceBar = document.createElement("div");
        confidenceBar.style.width = `${data.confidence * 100}%`;
        confidenceBar.style.height = "20px";
        confidenceBar.style.backgroundColor = data.confidence > 0.7 ? "green" : "orange";
        resultsContainer.appendChild(confidenceBar);

        const details = document.createElement("p");
        details.textContent = `Survival Rate: ${data.survival_rate * 100}%, Complication Risk: ${data.complication_risk * 100}%`;
        resultsContainer.appendChild(details);
    }

    // Example data for testing
    const exampleData = {
        survival_rate: 0.75,
        complication_risk: 0.2,
        confidence: 0.9
    };

    renderResults(exampleData);
});
