document.addEventListener("DOMContentLoaded", () => {
    const protocolVersionsContainer = document.getElementById("protocol-versions-container");
    const protocolVersionsList = document.getElementById("protocol-versions-list");
    const addProtocolVersionButton = document.getElementById("add-protocol-version");

    // Fetch and display protocol versions
    async function fetchProtocolVersions() {
        const response = await fetch("/api/protocol-versions");
        const protocolVersions = await response.json();

        protocolVersionsList.innerHTML = ""; // Clear existing list
        protocolVersions.forEach(version => {
            const listItem = document.createElement("li");
            listItem.textContent = `Version: ${version.version}, Date: ${version.date}`;
            protocolVersionsList.appendChild(listItem);
        });
    }

    // Add new protocol version
    addProtocolVersionButton.addEventListener("click", async () => {
        const newVersion = prompt("Enter new protocol version:");
        if (newVersion) {
            await fetch("/api/protocol-versions", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ version: newVersion })
            });
            fetchProtocolVersions();
        }
    });

    // Initial fetch
    fetchProtocolVersions();
});
