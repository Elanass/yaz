document.addEventListener("DOMContentLoaded", () => {
    const erasStepsContainer = document.getElementById("eras-protocol-container");
    const erasStepsList = document.getElementById("eras-steps-list");
    const addErasStepButton = document.getElementById("add-eras-step");

    // Fetch and display ERAS steps
    async function fetchErasSteps() {
        const response = await fetch("/api/eras-steps");
        const erasSteps = await response.json();

        erasStepsList.innerHTML = ""; // Clear existing list
        erasSteps.forEach(step => {
            const listItem = document.createElement("li");
            listItem.textContent = `Step: ${step.name}, Description: ${step.description}`;
            erasStepsList.appendChild(listItem);
        });
    }

    // Add new ERAS step
    addErasStepButton.addEventListener("click", async () => {
        const stepName = prompt("Enter step name:");
        const stepDescription = prompt("Enter step description:");
        if (stepName && stepDescription) {
            await fetch("/api/eras-steps", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: stepName, description: stepDescription })
            });
            fetchErasSteps();
        }
    });

    // Initial fetch
    fetchErasSteps();
});
