document.addEventListener("DOMContentLoaded", () => {
    const clientId = "client-123"; // Example client ID, replace with dynamic value if needed
    const wsUrl = `ws://${window.location.host}/ws/analytics/${clientId}`;
    const socket = new WebSocket(wsUrl);

    const riskScoreElement = document.getElementById("risk-score");
    const protocolAdherenceElement = document.getElementById("protocol-adherence");
    const qolMetricsElement = document.getElementById("qol-metrics");

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Update UI elements with real-time data
        riskScoreElement.textContent = `Risk Score: ${data.risk_score}`;
        protocolAdherenceElement.textContent = `Protocol Adherence: ${data.protocol_adherence}`;
        qolMetricsElement.textContent = `QoL Metrics: ${data.qol_metrics}`;
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
        console.warn("WebSocket connection closed.");
    };
});
