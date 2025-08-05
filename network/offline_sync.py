"""General platform offline sync wrapper for Bitchat."""
import json
import os
import queue
from datetime import datetime
from typing import List, Dict, Any

# Message queue for offline messages
message_queue = queue.Queue()
offline_storage_path = "/tmp/bitchat_offline_messages.json"


def queue_message(message: Dict[str, Any]) -> None:
    """Queue a message for offline sync."""
    timestamped_message = {
        **message,
        'timestamp': datetime.now().isoformat(),
        'status': 'queued'
    }
    message_queue.put(timestamped_message)
    _persist_queue()


def fetch_and_merge() -> List[Dict[str, Any]]:
    """Fetch queued messages and merge them."""
    messages = []
    _load_queue()
    
    while not message_queue.empty():
        message = message_queue.get()
        message['status'] = 'delivered'
        messages.append(message)
    
    _persist_queue()
    return messages


def get_queue_size() -> int:
    """Get the current size of the offline message queue."""
    return message_queue.qsize()


def clear_queue() -> None:
    """Clear all queued messages."""
    while not message_queue.empty():
        message_queue.get()
    _persist_queue()


def _persist_queue() -> None:
    """Persist the current queue to disk."""
    messages = []
    temp_queue = queue.Queue()
    
    # Extract all messages
    while not message_queue.empty():
        message = message_queue.get()
        messages.append(message)
        temp_queue.put(message)
    
    # Restore the queue
    while not temp_queue.empty():
        message_queue.put(temp_queue.get())
    
    # Save to file
    try:
        with open(offline_storage_path, 'w') as f:
            json.dump(messages, f, indent=2)
    except Exception as e:
        print(f"Failed to persist queue: {e}")


def _load_queue() -> None:
    """Load persisted messages back to the queue."""
    if not os.path.exists(offline_storage_path):
        return
    
    try:
        with open(offline_storage_path, 'r') as f:
            messages = json.load(f)
        
        # Clear current queue and reload
        while not message_queue.empty():
            message_queue.get()
        
        for message in messages:
            if message.get('status') == 'queued':
                message_queue.put(message)
                
    except Exception as e:
        print(f"Failed to load queue: {e}")
