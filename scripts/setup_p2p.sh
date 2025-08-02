#!/bin/bash
"""
P2P Network Setup Script for Gastric ADCI Platform
Automated setup for peer-to-peer collaborative environment
"""

set -e

echo "🔗 Setting up Gastric ADCI Platform - P2P Collaborative Network"

# Set environment variables for P2P mode
export GASTRIC_ADCI_ENV=p2p
export DEBUG=false
export LOG_LEVEL=INFO
export PORT=8000
export P2P_PORT=8765
export P2P_ENABLED=true
export DATA_DIR=./data/p2p
export DATABASE_URL=sqlite:///./data/p2p/gastric_adci.db

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_p2p() {
    echo -e "${PURPLE}[P2P]${NC} $1"
}

# Check P2P prerequisites
check_p2p_prerequisites() {
    print_status "Checking P2P prerequisites..."
    
    # Check Node.js for GUN.js (if using GUN for P2P)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_status "Node.js version: $NODE_VERSION"
    else
        print_warning "Node.js not found. P2P features may be limited."
    fi
    
    # Check network connectivity
    if command -v nc &> /dev/null; then
        print_status "Network tools available"
    else
        print_warning "Netcat not available. Network diagnostics will be limited."
    fi
}

# Setup P2P directories
setup_p2p_directories() {
    print_status "Setting up P2P directories..."
    
    mkdir -p data/p2p/database
    mkdir -p data/p2p/uploads
    mkdir -p data/p2p/sync
    mkdir -p data/p2p/peers
    mkdir -p data/p2p/logs
    mkdir -p logs/p2p
    
    print_success "P2P directories created"
}

# Install P2P dependencies
install_p2p_dependencies() {
    print_status "Installing P2P dependencies..."
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    elif [ -f "config/requirements.txt" ]; then
        pip install -r config/requirements.txt
    fi
    
    # Install additional P2P specific dependencies
    pip install websockets aiofiles cryptography
    
    # Install GUN.js if Node.js is available
    if command -v npm &> /dev/null; then
        print_status "Installing GUN.js for P2P networking..."
        if [ ! -d "node_modules" ]; then
            npm init -y
        fi
        npm install gun
        print_success "GUN.js installed"
    else
        print_warning "npm not available. Fallback P2P implementation will be used."
    fi
    
    print_success "P2P dependencies installed"
}

# Initialize P2P database
initialize_p2p_database() {
    print_status "Initializing P2P database..."
    
    python3 -c "
import sqlite3
import os
import json
from datetime import datetime

os.makedirs('data/p2p/database', exist_ok=True)
conn = sqlite3.connect('data/p2p/database/gastric_adci.db')

# Create P2P-specific tables
cursor = conn.cursor()

# Peer registry table
cursor.execute('''
CREATE TABLE IF NOT EXISTS peers (
    id TEXT PRIMARY KEY,
    address TEXT NOT NULL,
    port INTEGER,
    last_seen TIMESTAMP,
    public_key TEXT,
    status TEXT DEFAULT 'offline'
)
''')

# Sync log table
cursor.execute('''
CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    peer_id TEXT,
    data_type TEXT,
    sync_time TIMESTAMP,
    status TEXT,
    changes_count INTEGER
)
''')

conn.commit()
conn.close()

# Create peer identity file
peer_id = f'peer_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}'
peer_config = {
    'peer_id': peer_id,
    'created_at': datetime.now().isoformat(),
    'network': 'gastric-adci-p2p',
    'version': '2.0.0'
}

with open('data/p2p/peer_identity.json', 'w') as f:
    json.dump(peer_config, f, indent=2)

print('P2P database and identity initialized')
"
    
    print_success "P2P database initialized"
}

# Create P2P configuration
create_p2p_config() {
    print_status "Creating P2P configuration..."
    
    mkdir -p config
    
    # Generate random port for P2P if not specified
    P2P_PORT=${P2P_PORT:-$(shuf -i 8765-8999 -n 1)}
    
    cat > config/p2p.env << EOF
# P2P Network Configuration
GASTRIC_ADCI_ENV=p2p
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# P2P Network Settings
P2P_ENABLED=true
P2P_PORT=$P2P_PORT
PEER_DISCOVERY=gun
SYNC_INTERVAL=30
CONFLICT_RESOLUTION=last_write_wins

# Database (P2P distributed)
DATABASE_URL=sqlite:///./data/p2p/database/gastric_adci.db
P2P_STORAGE_PATH=./data/p2p

# File Storage
DATA_DIR=./data/p2p
FILE_STORAGE=./data/p2p/uploads

# Security
ENCRYPTION_ENABLED=true
AUTH_REQUIRED=true
SESSION_TIMEOUT=3600

# Collaboration Features
REAL_TIME_UPDATES=true
DATA_SHARING_ENABLED=true
FEEDBACK_COLLECTION=true
INSIGHT_SHARING=true
AUTOMATIC_SYNC=true
VERSION_CONTROL=true

# Network
BOOTSTRAP_NODES=
MAX_PEERS=10
EOF

    # Create GUN.js server configuration if Node.js is available
    if command -v node &> /dev/null; then
        cat > gun_server.js << EOF
// GUN.js P2P server for Gastric ADCI Platform
const Gun = require('gun');
const server = require('http').createServer();

const gun = Gun({
    web: server,
    file: 'data/p2p/gun_data'
});

const PORT = process.env.P2P_PORT || $P2P_PORT;

server.listen(PORT, () => {
    console.log(\`🔗 GUN.js P2P server running on port \${PORT}\`);
    console.log('Gastric ADCI P2P network ready for collaboration');
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
    console.log('Shutting down P2P server...');
    server.close();
});
EOF

        print_success "GUN.js server configuration created"
    fi
    
    print_success "P2P configuration created at config/p2p.env"
}

# Setup P2P network discovery
setup_p2p_discovery() {
    print_status "Setting up P2P network discovery..."
    
    # Create discovery script
    cat > scripts/p2p_discovery.py << 'EOF'
#!/usr/bin/env python3
"""
P2P Network Discovery for Gastric ADCI Platform
"""

import json
import socket
import threading
import time
from datetime import datetime

class P2PDiscovery:
    def __init__(self, port=8765):
        self.port = port
        self.peers = {}
        self.running = False
    
    def broadcast_presence(self):
        """Broadcast presence to local network"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        message = {
            "type": "gastric_adci_peer",
            "port": self.port,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            sock.sendto(json.dumps(message).encode(), ('<broadcast>', 9999))
            print(f"🔗 Broadcasted presence on port {self.port}")
        except Exception as e:
            print(f"❌ Broadcast failed: {e}")
        finally:
            sock.close()
    
    def listen_for_peers(self):
        """Listen for peer announcements"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 9999))
        
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                message = json.loads(data.decode())
                
                if message.get("type") == "gastric_adci_peer":
                    peer_id = f"{addr[0]}:{message['port']}"
                    self.peers[peer_id] = {
                        "address": addr[0],
                        "port": message["port"],
                        "last_seen": datetime.now().isoformat()
                    }
                    print(f"🤝 Discovered peer: {peer_id}")
            except Exception as e:
                if self.running:
                    print(f"❌ Discovery error: {e}")
    
    def start(self):
        """Start P2P discovery"""
        self.running = True
        
        # Start listener thread
        listener_thread = threading.Thread(target=self.listen_for_peers)
        listener_thread.daemon = True
        listener_thread.start()
        
        # Broadcast presence periodically
        while self.running:
            self.broadcast_presence()
            time.sleep(30)
    
    def stop(self):
        """Stop P2P discovery"""
        self.running = False

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    
    discovery = P2PDiscovery(port)
    try:
        print(f"🔍 Starting P2P discovery on port {port}")
        discovery.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping P2P discovery")
        discovery.stop()
EOF
    
    chmod +x scripts/p2p_discovery.py
    print_success "P2P discovery system created"
}

# Validate P2P setup
validate_p2p_setup() {
    print_status "Validating P2P setup..."
    
    # Check if ports are available
    if command -v nc &> /dev/null; then
        if nc -z localhost $PORT 2>/dev/null; then
            print_warning "Port $PORT is already in use"
        fi
        
        if nc -z localhost $P2P_PORT 2>/dev/null; then
            print_warning "P2P port $P2P_PORT is already in use"
        fi
    fi
    
    # Test P2P configuration
    python3 -c "
try:
    from core.config.environment import get_environment_config
    config = get_environment_config()
    
    if config.get_mode().value != 'p2p':
        print('❌ Environment not set to P2P mode')
        exit(1)
    
    if not config.p2p.enabled:
        print('❌ P2P not enabled in configuration')
        exit(1)
    
    print('✅ P2P configuration validation passed')
except Exception as e:
    print(f'❌ P2P validation failed: {e}')
    exit(1)
"
    
    print_success "P2P setup validation passed"
}

# Start P2P network
start_p2p_network() {
    print_status "Starting P2P network..."
    
    # Source P2P environment
    if [ -f "config/p2p.env" ]; then
        export $(cat config/p2p.env | grep -v '^#' | xargs)
    fi
    
    # Start GUN.js server if available
    if [ -f "gun_server.js" ] && command -v node &> /dev/null; then
        print_p2p "Starting GUN.js P2P server on port $P2P_PORT..."
        node gun_server.js &
        GUN_PID=$!
        sleep 2
    fi
    
    # Start P2P discovery
    print_p2p "Starting P2P discovery..."
    python3 scripts/p2p_discovery.py $P2P_PORT &
    DISCOVERY_PID=$!
    
    # Start main application
    print_p2p "Starting Gastric ADCI Platform in P2P mode..."
    print_status "Access the application at: http://localhost:$PORT"
    print_status "P2P network on port: $P2P_PORT"
    print_status ""
    print_status "Press Ctrl+C to stop all services"
    print_status ""
    
    # Cleanup function
    cleanup() {
        print_status "Shutting down P2P network..."
        if [ ! -z "$GUN_PID" ]; then
            kill $GUN_PID 2>/dev/null || true
        fi
        if [ ! -z "$DISCOVERY_PID" ]; then
            kill $DISCOVERY_PID 2>/dev/null || true
        fi
        exit 0
    }
    
    trap cleanup SIGINT SIGTERM
    
    # Start main application
    python3 main.py
}

# Main execution
main() {
    echo "════════════════════════════════════════════════════════════════"
    echo "🔗 Gastric ADCI Platform - P2P Network Setup"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    check_p2p_prerequisites
    setup_p2p_directories
    install_p2p_dependencies
    initialize_p2p_database
    create_p2p_config
    setup_p2p_discovery
    validate_p2p_setup
    
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    print_success "P2P network environment setup complete!"
    print_p2p "Ready for collaborative subject study!"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    # Ask if user wants to start the network
    read -p "Start the P2P network now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_p2p_network
    else
        echo ""
        print_status "To start the P2P network later, run:"
        print_status "  ./scripts/setup_p2p.sh start"
        print_status ""
        print_p2p "Share this command with collaborators to join the network:"
        print_p2p "  BOOTSTRAP_NODES=$(hostname -I | awk '{print $1}'):$P2P_PORT ./scripts/setup_p2p.sh start"
    fi
}

# Handle script arguments
case "${1:-setup}" in
    "setup")
        main
        ;;
    "start")
        print_status "Starting P2P network..."
        start_p2p_network
        ;;
    "validate")
        validate_p2p_setup
        ;;
    "clean")
        print_status "Cleaning P2P data..."
        rm -rf data/p2p/database/*.db
        rm -rf data/p2p/uploads/*
        rm -rf data/p2p/sync/*
        rm -rf data/p2p/peers/*
        print_success "P2P data cleaned"
        ;;
    "peers")
        print_p2p "Current peers:"
        if [ -f "data/p2p/peer_identity.json" ]; then
            cat data/p2p/peer_identity.json | jq .
        fi
        ;;
    *)
        echo "Usage: $0 {setup|start|validate|clean|peers}"
        echo "  setup    - Full P2P setup and optionally start"
        echo "  start    - Start the P2P network"
        echo "  validate - Validate P2P configuration"
        echo "  clean    - Clean P2P data"
        echo "  peers    - Show peer information"
        exit 1
        ;;
esac
