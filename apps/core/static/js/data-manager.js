/**
 * YAZ Data Manager - Real-time Data Synchronization
 * Handles data sync between backend, local storage, and real-time updates
 */

class YazDataManager {
    constructor(config = {}) {
        this.config = {
            apiBaseUrl: config.apiBaseUrl || '/api/v1',
            cacheExpiry: config.cacheExpiry || 300000, // 5 minutes
            retryAttempts: config.retryAttempts || 3,
            retryDelay: config.retryDelay || 1000,
            offlineMode: config.offlineMode || true,
            ...config
        };
        
        this.cache = new Map();
        this.subscriptions = new Map();
        this.eventListeners = new Map();
        this.isOnline = navigator.onLine;
        this.syncQueue = [];
        
        this.init();
    }
    
    init() {
        this.setupNetworkListeners();
        this.setupPeriodicSync();
        this.loadFromLocalStorage();
        
        // Initialize WebSocket connection if available
        if (window.yazWS) {
            this.setupWebSocketListeners();
        }
    }
    
    setupNetworkListeners() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            console.log('🌐 Back online - syncing data...');
            this.syncPendingData();
            this.emit('online');
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            console.log('📱 Offline mode activated');
            this.emit('offline');
        });
    }
    
    setupWebSocketListeners() {
        window.yazWS.on('data_update', (data) => {
            this.handleRealTimeUpdate(data);
        });
        
        window.yazWS.on('connected', () => {
            // Subscribe to real-time updates for active subscriptions
            this.subscriptions.forEach((callback, key) => {
                window.yazWS.subscribeToData(key, callback);
            });
        });
    }
    
    setupPeriodicSync() {
        setInterval(() => {
            if (this.isOnline) {
                this.syncCriticalData();
            }
        }, 30000); // Sync every 30 seconds
    }
    
    // Data fetching methods
    async get(endpoint, options = {}) {
        const { 
            cache = true, 
            realTime = false,
            fallbackToCache = true 
        } = options;
        
        const cacheKey = `${endpoint}_${JSON.stringify(options)}`;
        
        // Check cache first
        if (cache && this.hasValidCache(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }
        
        try {
            if (!this.isOnline && fallbackToCache) {
                return this.getFromLocalStorage(cacheKey);
            }
            
            const response = await this.makeRequest('GET', endpoint, null, options);
            
            if (cache) {
                this.setCache(cacheKey, response);
                this.saveToLocalStorage(cacheKey, response);
            }
            
            if (realTime) {
                this.subscribeToRealTimeUpdates(endpoint);
            }
            
            return response;
            
        } catch (error) {
            console.error(`❌ Failed to fetch ${endpoint}:`, error);
            
            if (fallbackToCache) {
                const cached = this.getFromLocalStorage(cacheKey);
                if (cached) {
                    console.log('📱 Using cached data due to network error');
                    return cached;
                }
            }
            
            throw error;
        }
    }
    
    async post(endpoint, data, options = {}) {
        return this.makeRequest('POST', endpoint, data, options);
    }
    
    async put(endpoint, data, options = {}) {
        return this.makeRequest('PUT', endpoint, data, options);
    }
    
    async delete(endpoint, options = {}) {
        return this.makeRequest('DELETE', endpoint, null, options);
    }
    
    async makeRequest(method, endpoint, data = null, options = {}) {
        const { retry = true } = options;
        
        if (!this.isOnline && this.config.offlineMode) {
            // Queue request for later
            this.queueRequest({ method, endpoint, data, options });
            throw new Error('Offline - request queued');
        }
        
        const url = `${this.config.apiBaseUrl}${endpoint}`;
        const requestOptions = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        if (data) {
            requestOptions.body = JSON.stringify(data);
        }
        
        let lastError;
        let attempt = 0;
        
        while (attempt < this.config.retryAttempts) {
            try {
                const response = await fetch(url, requestOptions);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                // Clear any queued requests for this endpoint on success
                this.clearQueuedRequests(endpoint);
                
                return result;
                
            } catch (error) {
                lastError = error;
                attempt++;
                
                if (attempt < this.config.retryAttempts && retry) {
                    console.log(`🔄 Retrying request to ${endpoint} (attempt ${attempt + 1})...`);
                    await this.delay(this.config.retryDelay * attempt);
                } else {
                    break;
                }
            }
        }
        
        throw lastError;
    }
    
    // Real-time data methods
    subscribeToRealTimeUpdates(dataType, callback) {
        this.subscriptions.set(dataType, callback);
        
        if (window.yazWS && window.yazWS.isConnected) {
            window.yazWS.subscribeToData(dataType, callback);
        }
    }
    
    unsubscribeFromRealTimeUpdates(dataType) {
        this.subscriptions.delete(dataType);
        
        if (window.yazWS) {
            window.yazWS.unsubscribeFromData(dataType);
        }
    }
    
    handleRealTimeUpdate(data) {
        const { type, payload } = data;
        
        // Update cache
        if (payload && type) {
            this.setCache(type, payload);
            this.saveToLocalStorage(type, payload);
        }
        
        // Notify subscribers
        if (this.subscriptions.has(type)) {
            this.subscriptions.get(type)(payload);
        }
        
        this.emit('realtime_update', { type, payload });
    }
    
    // Cache management
    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }
    
    hasValidCache(key) {
        if (!this.cache.has(key)) {
            return false;
        }
        
        const cached = this.cache.get(key);
        const age = Date.now() - cached.timestamp;
        
        return age < this.config.cacheExpiry;
    }
    
    clearCache(pattern = null) {
        if (pattern) {
            for (const key of this.cache.keys()) {
                if (key.includes(pattern)) {
                    this.cache.delete(key);
                }
            }
        } else {
            this.cache.clear();
        }
    }
    
    // Local storage methods
    saveToLocalStorage(key, data) {
        try {
            const item = {
                data,
                timestamp: Date.now()
            };
            localStorage.setItem(`yaz_${key}`, JSON.stringify(item));
        } catch (error) {
            console.warn('⚠️ Failed to save to localStorage:', error);
        }
    }
    
    getFromLocalStorage(key) {
        try {
            const item = localStorage.getItem(`yaz_${key}`);
            if (!item) return null;
            
            const parsed = JSON.parse(item);
            const age = Date.now() - parsed.timestamp;
            
            if (age < this.config.cacheExpiry) {
                return parsed.data;
            }
            
            // Remove expired item
            localStorage.removeItem(`yaz_${key}`);
            return null;
            
        } catch (error) {
            console.warn('⚠️ Failed to read from localStorage:', error);
            return null;
        }
    }
    
    loadFromLocalStorage() {
        try {
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.startsWith('yaz_')) {
                    const cleanKey = key.replace('yaz_', '');
                    const data = this.getFromLocalStorage(cleanKey);
                    if (data) {
                        this.setCache(cleanKey, data);
                    }
                }
            }
        } catch (error) {
            console.warn('⚠️ Failed to load from localStorage:', error);
        }
    }
    
    // Offline queue management
    queueRequest(request) {
        this.syncQueue.push({
            ...request,
            timestamp: Date.now()
        });
        
        console.log(`📝 Queued request: ${request.method} ${request.endpoint}`);
    }
    
    async syncPendingData() {
        if (this.syncQueue.length === 0) {
            return;
        }
        
        console.log(`🔄 Syncing ${this.syncQueue.length} queued requests...`);
        
        const queue = [...this.syncQueue];
        this.syncQueue = [];
        
        for (const request of queue) {
            try {
                await this.makeRequest(
                    request.method,
                    request.endpoint,
                    request.data,
                    { ...request.options, retry: false }
                );
                console.log(`✅ Synced: ${request.method} ${request.endpoint}`);
            } catch (error) {
                console.error(`❌ Failed to sync: ${request.method} ${request.endpoint}`, error);
                // Re-queue failed requests
                this.syncQueue.push(request);
            }
        }
    }
    
    clearQueuedRequests(endpoint) {
        this.syncQueue = this.syncQueue.filter(req => req.endpoint !== endpoint);
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
    
    // Utility methods
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    async syncCriticalData() {
        const criticalEndpoints = [
            '/dashboard/stats',
            '/dashboard/activity'
        ];
        
        for (const endpoint of criticalEndpoints) {
            try {
                await this.get(endpoint, { cache: true });
            } catch (error) {
                console.warn(`⚠️ Failed to sync critical data: ${endpoint}`);
            }
        }
    }
    
    // Healthcare-specific methods
    async getPatients(options = {}) {
        return this.get('/patients', { ...options, realTime: true });
    }
    
    async getProcedures(options = {}) {
        return this.get('/procedures', { ...options, realTime: true });
    }
    
    async getActivity(options = {}) {
        return this.get('/dashboard/activity', { ...options, realTime: true });
    }
    
    async getDashboardStats(options = {}) {
        return this.get('/dashboard/stats', { ...options, realTime: true });
    }
    
    async submitProcedureData(data) {
        const result = await this.post('/procedures', data);
        
        // Trigger real-time update
        if (window.yazWS) {
            window.yazWS.updateData('procedures', result);
        }
        
        return result;
    }
    
    async updatePatient(id, data) {
        const result = await this.put(`/patients/${id}`, data);
        
        // Trigger real-time update
        if (window.yazWS) {
            window.yazWS.updateData('patients', result);
        }
        
        return result;
    }
}

// Export and initialize
window.YazDataManager = YazDataManager;
window.yazData = new YazDataManager();
