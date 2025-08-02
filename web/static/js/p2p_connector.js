/**
 * P2P WebRTC Connector for Gastric ADCI Platform
 * Handles peer-to-peer connections for real-time collaboration
 */

class P2PConnector {
    constructor(signalingServerUrl = 'ws://localhost:8000/p2p/ws/peer') {
        this.signalingServerUrl = signalingServerUrl;
        this.signalingSocket = null;
        this.peerId = null;
        this.currentRoom = null;
        this.peerConnections = new Map(); // peer_id -> RTCPeerConnection
        this.dataChannels = new Map(); // peer_id -> RTCDataChannel
        this.activePeers = new Set();
        this.connectionState = 'disconnected';
        this.eventHandlers = new Map();
        
        // WebRTC configuration
        this.rtcConfig = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ],
            iceCandidatePoolSize: 10
        };
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('Initializing P2P Connector');
        
        // Check WebRTC support
        if (!this.checkWebRTCSupport()) {
            console.error('WebRTC not supported in this browser');
            this.emit('error', { message: 'WebRTC not supported' });
            return;
        }
        
        // Connect to signaling server
        this.connectToSignaling();
        
        // Setup periodic heartbeat
        this.setupHeartbeat();
    }
    
    checkWebRTCSupport() {
        return !!(window.RTCPeerConnection && 
                 window.RTCSessionDescription && 
                 window.RTCIceCandidate);
    }
    
    connectToSignaling() {
        try {
            this.signalingSocket = new WebSocket(this.signalingServerUrl);
            
            this.signalingSocket.onopen = () => {
                console.log('Connected to signaling server');
                this.connectionState = 'signaling_connected';
                this.emit('signaling_connected');
            };
            
            this.signalingSocket.onmessage = (event) => {
                this.handleSignalingMessage(JSON.parse(event.data));
            };
            
            this.signalingSocket.onclose = () => {
                console.log('Disconnected from signaling server');
                this.connectionState = 'disconnected';
                this.emit('signaling_disconnected');
                
                // Attempt reconnection after delay
                setTimeout(() => {
                    if (this.connectionState === 'disconnected') {
                        this.connectToSignaling();
                    }
                }, 5000);
            };
            
            this.signalingSocket.onerror = (error) => {
                console.error('Signaling socket error:', error);
                this.emit('error', { message: 'Signaling connection failed' });
            };
            
        } catch (error) {
            console.error('Failed to connect to signaling server:', error);
            this.emit('error', { message: 'Failed to connect to signaling server' });
        }
    }
    
    async handleSignalingMessage(message) {
        console.log('Received signaling message:', message.type);
        
        switch (message.type) {
            case 'connection_established':
                this.peerId = message.peer_id;
                this.emit('peer_id_assigned', { peer_id: this.peerId });
                break;
                
            case 'room_joined':
                this.currentRoom = message.room_id;
                this.emit('room_joined', message);
                break;
                
            case 'peer_joined':
                this.activePeers.add(message.peer_id);
                this.emit('peer_joined', message);
                // Initiate connection to new peer
                await this.initiateConnection(message.peer_id);
                break;
                
            case 'peer_left':
            case 'peer_disconnected':
                this.activePeers.delete(message.peer_id);
                this.closePeerConnection(message.peer_id);
                this.emit('peer_left', message);
                break;
                
            case 'offer':
                await this.handleOffer(message);
                break;
                
            case 'answer':
                await this.handleAnswer(message);
                break;
                
            case 'ice_candidate':
                await this.handleIceCandidate(message);
                break;
                
            case 'data_sync':
                this.emit('data_sync', message);
                break;
                
            case 'heartbeat_ack':
                // Heartbeat acknowledged
                break;
                
            case 'error':
                console.error('Signaling error:', message.error);
                this.emit('error', message);
                break;
                
            case 'server_shutdown':
                console.warn('Signaling server shutting down');
                this.emit('server_shutdown', message);
                break;
        }
    }
    
    async joinRoom(roomId, metadata = {}) {
        if (this.connectionState !== 'signaling_connected') {
            throw new Error('Not connected to signaling server');
        }
        
        const message = {
            type: 'join_room',
            room_id: roomId,
            metadata: {
                user_id: metadata.user_id || 'anonymous',
                user_name: metadata.user_name || 'Anonymous User',
                ...metadata
            }
        };
        
        this.sendSignalingMessage(message);
    }
    
    async leaveRoom() {
        if (!this.currentRoom) {
            return;
        }
        
        // Close all peer connections
        for (const [peerId, _] of this.peerConnections) {
            this.closePeerConnection(peerId);
        }
        
        const message = {
            type: 'leave_room',
            room_id: this.currentRoom
        };
        
        this.sendSignalingMessage(message);
        this.currentRoom = null;
        this.activePeers.clear();
    }
    
    async initiateConnection(targetPeerId) {
        console.log(`Initiating connection to peer ${targetPeerId}`);
        
        try {
            const peerConnection = this.createPeerConnection(targetPeerId);
            
            // Create data channel
            const dataChannel = peerConnection.createDataChannel('gastric_adci_data', {
                ordered: true
            });
            
            this.setupDataChannel(targetPeerId, dataChannel);
            
            // Create offer
            const offer = await peerConnection.createOffer();
            await peerConnection.setLocalDescription(offer);
            
            // Send offer through signaling
            this.sendSignalingMessage({
                type: 'offer',
                target_peer_id: targetPeerId,
                offer: offer
            });
            
        } catch (error) {
            console.error(`Failed to initiate connection to ${targetPeerId}:`, error);
            this.emit('connection_failed', { peer_id: targetPeerId, error: error.message });
        }
    }
    
    async handleOffer(message) {
        const fromPeerId = message.from_peer_id;
        console.log(`Handling offer from peer ${fromPeerId}`);
        
        try {
            const peerConnection = this.createPeerConnection(fromPeerId);
            
            await peerConnection.setRemoteDescription(message.offer);
            
            // Create answer
            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);
            
            // Send answer through signaling
            this.sendSignalingMessage({
                type: 'answer',
                target_peer_id: fromPeerId,
                answer: answer
            });
            
        } catch (error) {
            console.error(`Failed to handle offer from ${fromPeerId}:`, error);
            this.emit('connection_failed', { peer_id: fromPeerId, error: error.message });
        }
    }
    
    async handleAnswer(message) {
        const fromPeerId = message.from_peer_id;
        console.log(`Handling answer from peer ${fromPeerId}`);
        
        try {
            const peerConnection = this.peerConnections.get(fromPeerId);
            if (peerConnection) {
                await peerConnection.setRemoteDescription(message.answer);
            }
        } catch (error) {
            console.error(`Failed to handle answer from ${fromPeerId}:`, error);
        }
    }
    
    async handleIceCandidate(message) {
        const fromPeerId = message.from_peer_id;
        
        try {
            const peerConnection = this.peerConnections.get(fromPeerId);
            if (peerConnection && message.candidate) {
                await peerConnection.addIceCandidate(message.candidate);
            }
        } catch (error) {
            console.error(`Failed to handle ICE candidate from ${fromPeerId}:`, error);
        }
    }
    
    createPeerConnection(peerId) {
        const peerConnection = new RTCPeerConnection(this.rtcConfig);
        this.peerConnections.set(peerId, peerConnection);
        
        // Handle ICE candidates
        peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.sendSignalingMessage({
                    type: 'ice_candidate',
                    target_peer_id: peerId,
                    candidate: event.candidate
                });
            }
        };
        
        // Handle connection state changes
        peerConnection.onconnectionstatechange = () => {
            console.log(`Peer ${peerId} connection state: ${peerConnection.connectionState}`);
            
            if (peerConnection.connectionState === 'connected') {
                this.emit('peer_connected', { peer_id: peerId });
            } else if (peerConnection.connectionState === 'failed' || 
                      peerConnection.connectionState === 'disconnected') {
                this.closePeerConnection(peerId);
                this.emit('peer_disconnected', { peer_id: peerId });
            }
        };
        
        // Handle incoming data channels
        peerConnection.ondatachannel = (event) => {
            this.setupDataChannel(peerId, event.channel);
        };
        
        return peerConnection;
    }
    
    setupDataChannel(peerId, dataChannel) {
        this.dataChannels.set(peerId, dataChannel);
        
        dataChannel.onopen = () => {
            console.log(`Data channel opened with peer ${peerId}`);
            this.emit('data_channel_opened', { peer_id: peerId });
        };
        
        dataChannel.onclose = () => {
            console.log(`Data channel closed with peer ${peerId}`);
            this.dataChannels.delete(peerId);
            this.emit('data_channel_closed', { peer_id: peerId });
        };
        
        dataChannel.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.emit('peer_data', { peer_id: peerId, data: data });
            } catch (error) {
                console.error(`Failed to parse data from peer ${peerId}:`, error);
            }
        };
        
        dataChannel.onerror = (error) => {
            console.error(`Data channel error with peer ${peerId}:`, error);
            this.emit('data_channel_error', { peer_id: peerId, error: error });
        };
    }
    
    closePeerConnection(peerId) {
        const peerConnection = this.peerConnections.get(peerId);
        if (peerConnection) {
            peerConnection.close();
            this.peerConnections.delete(peerId);
        }
        
        if (this.dataChannels.has(peerId)) {
            this.dataChannels.delete(peerId);
        }
    }
    
    // Send data to specific peer
    sendToPeer(peerId, data) {
        const dataChannel = this.dataChannels.get(peerId);
        if (dataChannel && dataChannel.readyState === 'open') {
            try {
                dataChannel.send(JSON.stringify(data));
                return true;
            } catch (error) {
                console.error(`Failed to send data to peer ${peerId}:`, error);
            }
        }
        return false;
    }
    
    // Broadcast data to all connected peers
    broadcast(data) {
        let sentCount = 0;
        for (const [peerId, dataChannel] of this.dataChannels) {
            if (dataChannel.readyState === 'open') {
                if (this.sendToPeer(peerId, data)) {
                    sentCount++;
                }
            }
        }
        return sentCount;
    }
    
    // Send data sync through signaling (for reliability)
    syncData(data, syncType = 'general') {
        this.sendSignalingMessage({
            type: 'data_sync',
            data: data,
            sync_type: syncType
        });
    }
    
    sendSignalingMessage(message) {
        if (this.signalingSocket && this.signalingSocket.readyState === WebSocket.OPEN) {
            this.signalingSocket.send(JSON.stringify(message));
            return true;
        }
        return false;
    }
    
    setupHeartbeat() {
        setInterval(() => {
            if (this.connectionState === 'signaling_connected') {
                this.sendSignalingMessage({
                    type: 'heartbeat',
                    timestamp: new Date().toISOString()
                });
            }
        }, 30000); // Every 30 seconds
    }
    
    // Event system
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }
    
    off(event, handler) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }
    
    emit(event, data = null) {
        if (this.eventHandlers.has(event)) {
            this.eventHandlers.get(event).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }
    
    // Get current status
    getStatus() {
        return {
            peer_id: this.peerId,
            current_room: this.currentRoom,
            connection_state: this.connectionState,
            active_peers: Array.from(this.activePeers),
            connected_peers: Array.from(this.dataChannels.keys()).filter(
                peerId => this.dataChannels.get(peerId).readyState === 'open'
            ),
            peer_connections: this.peerConnections.size,
            data_channels: this.dataChannels.size
        };
    }
    
    // Disconnect and cleanup
    disconnect() {
        this.leaveRoom();
        
        if (this.signalingSocket) {
            this.signalingSocket.close();
            this.signalingSocket = null;
        }
        
        this.connectionState = 'disconnected';
        this.peerId = null;
        this.currentRoom = null;
        this.activePeers.clear();
        
        this.emit('disconnected');
    }
}

// Integration with existing Gun.js if available
if (window.GastricADCI && window.GastricADCI.Gun) {
    window.GastricADCI.P2P = {
        connector: null,
        
        init(userMetadata = {}) {
            this.connector = new P2PConnector();
            
            // Setup event handlers for Gun.js integration
            this.connector.on('peer_data', (event) => {
                this.handlePeerData(event.peer_id, event.data);
            });
            
            this.connector.on('data_sync', (event) => {
                this.handleDataSync(event);
            });
            
            return this.connector;
        },
        
        handlePeerData(peerId, data) {
            // Integrate with Gun.js for data synchronization
            if (data.type === 'gun_sync' && window.GastricADCI.Gun) {
                // Handle Gun.js data synchronization
                console.log('Received Gun.js sync data from peer:', peerId);
            }
        },
        
        handleDataSync(event) {
            // Handle data synchronization through signaling
            console.log('Received data sync:', event.sync_type, event.data);
        },
        
        joinCollaborativeSpace(spaceId, userMetadata = {}) {
            if (this.connector) {
                return this.connector.joinRoom(spaceId, userMetadata);
            }
        },
        
        getConnector() {
            return this.connector;
        }
    };
} else {
    // Standalone initialization
    window.GastricADCI = window.GastricADCI || {};
    window.GastricADCI.P2P = new P2PConnector();
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = P2PConnector;
}
