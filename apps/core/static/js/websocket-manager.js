/**
 * YAZ WebSocket Manager - Real-time P2P Communication
 * Handles WebSocket connections, real-time data sync, and mobile connectivity
 */

class YazWebSocketManager {
    constructor(config = {}) {
        this.config = {
            url: config.url || `ws://${window.location.host}/ws`,
            reconnectInterval: config.reconnectInterval || 3000,
            maxReconnectAttempts: config.maxReconnectAttempts || 10,
            heartbeatInterval: config.heartbeatInterval || 30000,
            ...config
        };
        
        this.ws = null;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.messageQueue = [];
        this.eventListeners = new Map();
        this.heartbeatTimer = null;
        this.clientId = this.generateClientId();
        
        this.init();
    }
    
    generateClientId() {
        return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    init() {
        this.connect();
        this.setupHeartbeat();
        
        // Handle page visibility changes for mobile optimization
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseHeartbeat();
            } else {
                this.resumeHeartbeat();
                if (!this.isConnected) {
                    this.connect();
                }
            }
        });
        
        // Handle network status changes
        window.addEventListener('online', () => {
            console.log('🌐 Network online - reconnecting...');
            this.connect();
        });
        
        window.addEventListener('offline', () => {
            console.log('📱 Network offline - entering offline mode');
            this.handleOfflineMode();
        });
    }
    
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
            return;
        }
        
        try {
            console.log(`🔌 Connecting to ${this.config.url}...`);
            this.ws = new WebSocket(this.config.url);
            
            this.ws.onopen = (event) => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                
                // Send identification message
                this.send({
                    type: 'client_identify',
                    clientId: this.clientId,
                    userAgent: navigator.userAgent,
                    timestamp: Date.now()
                });
                
                // Process queued messages
                this.processMessageQueue();
                
                this.emit('connected', { clientId: this.clientId });
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.ws.onclose = (event) => {
                console.log('🔌 WebSocket disconnected:', event.reason);
                this.isConnected = false;
                this.emit('disconnected', { reason: event.reason });
                
                if (!event.wasClean && this.reconnectAttempts < this.config.maxReconnectAttempts) {
                    this.scheduleReconnect();
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.emit('error', error);
            };
            
        } catch (error) {
            console.error('❌ Failed to create WebSocket connection:', error);
            this.scheduleReconnect();
        }
    }
    
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            
            // Handle system messages
            switch (message.type) {
                case 'heartbeat':
                    this.send({ type: 'heartbeat_ack', timestamp: Date.now() });
                    break;
                case 'client_count':
                    this.emit('client_count_update', message.data);
                    break;
                case 'real_time_data':
                    this.emit('data_update', message.data);
                    break;
                case 'notification':
                    this.showNotification(message.data);
                    break;
                default:
                    this.emit('message', message);
            }
            
            // Emit specific event type
            if (message.type) {
                this.emit(message.type, message.data || message);
            }
            
        } catch (error) {
            console.error('❌ Failed to parse WebSocket message:', error);
        }
    }
    
    send(data) {
        const message = {
            ...data,
            clientId: this.clientId,
            timestamp: Date.now()
        };
        
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            // Queue message for later
            this.messageQueue.push(message);
            console.log('📝 Message queued (not connected)');
        }
    }
    
    processMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.ws.send(JSON.stringify(message));
        }
    }
    
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.config.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1);
        
        console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }
    
    setupHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'heartbeat' });
            }
        }, this.config.heartbeatInterval);
    }
    
    pauseHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
        }
    }
    
    resumeHeartbeat() {
        this.setupHeartbeat();
    }
    
    handleOfflineMode() {
        // Store data locally when offline
        this.emit('offline_mode', { 
            queuedMessages: this.messageQueue.length 
        });
    }
    
    showNotification(data) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(data.title || 'YAZ Healthcare', {
                body: data.message,
                icon: '/static/assets/logo.png',
                badge: '/static/assets/badge.png'
            });
        }
        
        this.emit('notification', data);
    }
    
    // Event system
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }
    
    off(event, callback) {
        if (this.eventListeners.has(event)) {
            const listeners = this.eventListeners.get(event);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }
    
    emit(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`❌ Error in event listener for ${event}:`, error);
                }
            });
        }
    }
    
    // Real-time data methods
    subscribeToData(dataType, callback) {
        this.on(`data_${dataType}`, callback);
        this.send({
            type: 'subscribe',
            dataType: dataType
        });
    }
    
    unsubscribeFromData(dataType) {
        this.send({
            type: 'unsubscribe',
            dataType: dataType
        });
    }
    
    updateData(dataType, data) {
        this.send({
            type: 'data_update',
            dataType: dataType,
            data: data
        });
    }
    
    // Mobile-specific methods
    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                console.log('📱 Notification permission:', permission);
            });
        }
    }
    
    enableMobileOptimization() {
        // Reduce heartbeat frequency on mobile
        if (/Mobile|Android|iPhone/i.test(navigator.userAgent)) {
            this.config.heartbeatInterval = 60000; // 1 minute for mobile
            console.log('📱 Mobile optimization enabled');
        }
    }
    
    disconnect() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
        }
        
        if (this.ws) {
            this.ws.close(1000, 'Client disconnect');
        }
        
        this.isConnected = false;
    }
}

// Export for global use
window.YazWebSocketManager = YazWebSocketManager;

// Auto-initialize if not in module environment
if (typeof module === 'undefined') {
    window.yazWS = new YazWebSocketManager();
}
