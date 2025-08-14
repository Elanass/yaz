"""Surgify Communication API using Bitchat mesh networking."""

import logging

from flask import Flask, jsonify, request

from apps.surge.network import get_surgify_handler, initialize_surgify_network


app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize Surgify networking on startup
surgify_handler = initialize_surgify_network("surgify_node_1")


@app.route("/message/send", methods=["POST"])
def send_message():
    """Send a message via Bitchat mesh network with Surgify-specific handling."""
    try:
        data = request.json

        # Validate required fields
        if not all(key in data for key in ["destination", "message"]):
            return (
                jsonify({"error": "Missing required fields: destination, message"}),
                400,
            )

        handler = get_surgify_handler()
        if not handler:
            return jsonify({"error": "Surgify network not initialized"}), 500

        # Determine message type and send accordingly
        message_type = data.get("type", "medical_data")

        if message_type == "case_consultation":
            success = handler.send_case_consultation(
                data["destination"], data.get("case_id", ""), data["message"]
            )
        else:
            success = handler.send_medical_data(data["destination"], data["message"])

        if success:
            return jsonify({"status": "Message sent successfully"})
        return jsonify({"status": "Message queued for offline sync"})

    except Exception as e:
        logger.exception(f"Failed to send message: {e}")
        return jsonify({"error": "Failed to send message"}), 500


@app.route("/message/sync", methods=["GET"])
def sync_messages():
    """Sync offline messages and retrieve incoming messages."""
    try:
        handler = get_surgify_handler()
        if not handler:
            return jsonify({"error": "Surgify network not initialized"}), 500

        # Sync offline messages
        offline_synced = handler.sync_offline_messages()

        # Receive new messages
        incoming_messages = handler.receive_messages()

        return jsonify(
            {
                "incoming_messages": incoming_messages,
                "offline_synced": offline_synced,
                "total_messages": len(incoming_messages) + len(offline_synced),
            }
        )

    except Exception as e:
        logger.exception(f"Failed to sync messages: {e}")
        return jsonify({"error": "Failed to sync messages"}), 500


@app.route("/network/status", methods=["GET"])
def network_status():
    """Get network status and peer information."""
    try:
        # Import here to avoid circular imports
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../"))
        from network import get_peers, get_queue_size

        peers = get_peers()
        queue_size = get_queue_size()

        handler = get_surgify_handler()
        node_id = handler.node_id if handler else "unknown"

        return jsonify(
            {
                "node_id": node_id,
                "connected_peers": peers,
                "offline_queue_size": queue_size,
                "status": "online" if peers else "offline",
            }
        )

    except Exception as e:
        logger.exception(f"Failed to get network status: {e}")
        return jsonify({"error": "Failed to get network status"}), 500


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, host="0.0.0.0", port=5000)
