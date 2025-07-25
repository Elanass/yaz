/**
 * Post-Op Monitoring Module for Gastric ADCI Platform
 * HIPAA/GDPR Compliant patient monitoring with offline-first capabilities
 */

class PostOpMonitoring {
    constructor() {
        this.patientData = null;
        this.metrics = {
            pain: [],
            temperature: [],
            bloodPressure: [],
            heartRate: [],
            respiratoryRate: [],
            oxygenSaturation: [],
            drainOutput: [],
            woundStatus: []
        };
        this.alertThresholds = {
            pain: 7, // On scale of 1-10
            temperature: 38.5, // Celsius
            highBloodPressure: 140, // Systolic
            lowBloodPressure: 90, // Systolic
            heartRate: { high: 100, low: 50 },
            respiratoryRate: { high: 24, low: 8 },
            oxygenSaturation: 92, // Percent
            drainOutput: 200 // mL in 24hr period
        };
        this.notificationPermission = false;
        this.syncStatus = 'online';
        this.dbInstance = null;
        
        // Initialize module
        this.init();
    }
    
    async init() {
        // Set up IndexedDB for offline storage
        await this.setupDatabase();
        
        // Request notification permissions
        this.requestNotificationPermission();
        
        // Set up listeners for offline/online status
        window.addEventListener('online', () => {
            this.syncStatus = 'online';
            this.syncOfflineData();
        });
        
        window.addEventListener('offline', () => {
            this.syncStatus = 'offline';
            this.showOfflineNotification();
        });
        
        // Listen for incoming patient data
        document.addEventListener('postOpData', this.handleIncomingData.bind(this));
        
        console.log('Post-Op Monitoring module initialized');
    }
    
    async setupDatabase() {
        return new Promise((resolve, reject) => {
            const request = window.indexedDB.open('postOpMonitoringDB', 1);
            
            request.onerror = (event) => {
                console.error('IndexedDB error:', event.target.error);
                reject(event.target.error);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Create object stores for different metrics
                const patientStore = db.createObjectStore('patients', { keyPath: 'id' });
                patientStore.createIndex('by_mrn', 'mrn', { unique: true });
                
                const metricsStore = db.createObjectStore('metrics', { keyPath: 'id', autoIncrement: true });
                metricsStore.createIndex('by_patient_id', 'patientId', { unique: false });
                metricsStore.createIndex('by_timestamp', 'timestamp', { unique: false });
                metricsStore.createIndex('by_metric_type', 'metricType', { unique: false });
                
                const alertsStore = db.createObjectStore('alerts', { keyPath: 'id', autoIncrement: true });
                alertsStore.createIndex('by_patient_id', 'patientId', { unique: false });
                alertsStore.createIndex('by_timestamp', 'timestamp', { unique: false });
                alertsStore.createIndex('by_status', 'status', { unique: false });
                
                // Create audit log store (HIPAA requirement)
                const auditStore = db.createObjectStore('audit', { keyPath: 'id', autoIncrement: true });
                auditStore.createIndex('by_user', 'userId', { unique: false });
                auditStore.createIndex('by_action', 'action', { unique: false });
                auditStore.createIndex('by_timestamp', 'timestamp', { unique: false });
            };
            
            request.onsuccess = (event) => {
                this.dbInstance = event.target.result;
                console.log('IndexedDB setup successful');
                resolve();
            };
        });
    }
    
    requestNotificationPermission() {
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                this.notificationPermission = permission === 'granted';
            });
        }
    }
    
    async handleIncomingData(event) {
        const data = event.detail;
        
        // Validate incoming data
        if (!this.validateMetricData(data)) {
            console.error('Invalid metric data received:', data);
            this.logAudit('data_validation_error', data);
            return;
        }
        
        // Store data locally first (offline-first approach)
        await this.storeMetricData(data);
        
        // Update charts and visualizations
        this.updateVisualizations(data);
        
        // Check for clinical alerts
        this.checkAlertThresholds(data);
        
        // Try to sync with server if online
        if (this.syncStatus === 'online') {
            this.syncDataWithServer(data);
        }
        
        // Log this action for HIPAA audit
        this.logAudit('metric_recorded', {
            patientId: data.patientId,
            metricType: data.metricType,
            timestamp: data.timestamp
        });
    }
    
    validateMetricData(data) {
        // Ensure required fields exist
        if (!data.patientId || !data.metricType || !data.value || !data.timestamp) {
            return false;
        }
        
        // Specific validation rules per metric type
        switch (data.metricType) {
            case 'pain':
                return data.value >= 0 && data.value <= 10;
            case 'temperature':
                return data.value >= 35 && data.value <= 43; // Valid clinical range
            case 'bloodPressure':
                return data.value.systolic && data.value.diastolic &&
                       data.value.systolic >= 70 && data.value.systolic <= 220 &&
                       data.value.diastolic >= 40 && data.value.diastolic <= 120;
            case 'heartRate':
                return data.value >= 30 && data.value <= 200;
            case 'respiratoryRate':
                return data.value >= 5 && data.value <= 60;
            case 'oxygenSaturation':
                return data.value >= 70 && data.value <= 100;
            case 'drainOutput':
                return data.value >= 0 && data.value <= 2000;
            case 'woundStatus':
                return ['normal', 'redness', 'swelling', 'discharge', 'dehiscence'].includes(data.value);
            default:
                return false;
        }
    }
    
    async storeMetricData(data) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['metrics'], 'readwrite');
            const store = transaction.objectStore('metrics');
            
            const request = store.add({
                patientId: data.patientId,
                metricType: data.metricType,
                value: data.value,
                timestamp: data.timestamp,
                recordedBy: data.recordedBy || 'unknown',
                notes: data.notes || '',
                source: data.source || 'manual',
                syncStatus: 'pending'
            });
            
            request.onsuccess = () => resolve();
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    updateVisualizations(data) {
        // Dispatch event for charts to update
        const event = new CustomEvent('postOpVisualizationUpdate', {
            detail: {
                metricType: data.metricType,
                data: data
            }
        });
        document.dispatchEvent(event);
        
        // Update metrics array for local visualizations
        if (this.metrics[data.metricType]) {
            this.metrics[data.metricType].push(data);
            
            // Keep only last 100 readings for performance
            if (this.metrics[data.metricType].length > 100) {
                this.metrics[data.metricType].shift();
            }
        }
    }
    
    checkAlertThresholds(data) {
        let alertTriggered = false;
        let alertMessage = '';
        
        switch (data.metricType) {
            case 'pain':
                if (data.value >= this.alertThresholds.pain) {
                    alertTriggered = true;
                    alertMessage = `High pain level (${data.value}/10) detected`;
                }
                break;
            case 'temperature':
                if (data.value >= this.alertThresholds.temperature) {
                    alertTriggered = true;
                    alertMessage = `Elevated temperature (${data.value}°C) detected`;
                }
                break;
            case 'bloodPressure':
                if (data.value.systolic >= this.alertThresholds.highBloodPressure) {
                    alertTriggered = true;
                    alertMessage = `High blood pressure (${data.value.systolic}/${data.value.diastolic} mmHg) detected`;
                } else if (data.value.systolic <= this.alertThresholds.lowBloodPressure) {
                    alertTriggered = true;
                    alertMessage = `Low blood pressure (${data.value.systolic}/${data.value.diastolic} mmHg) detected`;
                }
                break;
            case 'heartRate':
                if (data.value >= this.alertThresholds.heartRate.high) {
                    alertTriggered = true;
                    alertMessage = `Elevated heart rate (${data.value} bpm) detected`;
                } else if (data.value <= this.alertThresholds.heartRate.low) {
                    alertTriggered = true;
                    alertMessage = `Low heart rate (${data.value} bpm) detected`;
                }
                break;
            case 'respiratoryRate':
                if (data.value >= this.alertThresholds.respiratoryRate.high) {
                    alertTriggered = true;
                    alertMessage = `Elevated respiratory rate (${data.value} breaths/min) detected`;
                } else if (data.value <= this.alertThresholds.respiratoryRate.low) {
                    alertTriggered = true;
                    alertMessage = `Low respiratory rate (${data.value} breaths/min) detected`;
                }
                break;
            case 'oxygenSaturation':
                if (data.value <= this.alertThresholds.oxygenSaturation) {
                    alertTriggered = true;
                    alertMessage = `Low oxygen saturation (${data.value}%) detected`;
                }
                break;
            case 'drainOutput':
                if (data.value >= this.alertThresholds.drainOutput) {
                    alertTriggered = true;
                    alertMessage = `High drain output (${data.value} mL) detected`;
                }
                break;
            case 'woundStatus':
                if (data.value !== 'normal') {
                    alertTriggered = true;
                    alertMessage = `Abnormal wound status (${data.value}) detected`;
                }
                break;
        }
        
        if (alertTriggered) {
            this.triggerClinicalAlert(data.patientId, alertMessage, data);
        }
    }
    
    async triggerClinicalAlert(patientId, message, data) {
        // Store alert in IndexedDB
        const alertData = {
            patientId: patientId,
            message: message,
            metricType: data.metricType,
            metricValue: data.value,
            timestamp: new Date().toISOString(),
            status: 'unacknowledged',
            priority: this.calculateAlertPriority(data)
        };
        
        // Save to local DB
        await this.storeAlert(alertData);
        
        // Show notification if permitted
        if (this.notificationPermission) {
            new Notification('Clinical Alert', {
                body: `Patient ${patientId}: ${message}`,
                icon: '/static/img/alert-icon.png',
                tag: `alert-${patientId}-${data.metricType}`,
                requireInteraction: true
            });
        }
        
        // Display on UI
        this.displayAlertOnUI(alertData);
        
        // If online, send to server
        if (this.syncStatus === 'online') {
            this.syncAlertWithServer(alertData);
        }
        
        // Log this alert for HIPAA audit
        this.logAudit('alert_triggered', {
            patientId: patientId,
            alertType: data.metricType,
            severity: alertData.priority
        });
    }
    
    calculateAlertPriority(data) {
        // Determine alert priority based on clinical rules
        let priority = 'medium';
        
        switch (data.metricType) {
            case 'oxygenSaturation':
                if (data.value < 90) priority = 'high';
                else if (data.value < 94) priority = 'medium';
                else priority = 'low';
                break;
            case 'pain':
                if (data.value >= 9) priority = 'high';
                else if (data.value >= 7) priority = 'medium';
                else priority = 'low';
                break;
            case 'temperature':
                if (data.value >= 39.5) priority = 'high';
                else if (data.value >= 38.5) priority = 'medium';
                else priority = 'low';
                break;
            // Add rules for other metrics
        }
        
        return priority;
    }
    
    async storeAlert(alertData) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['alerts'], 'readwrite');
            const store = transaction.objectStore('alerts');
            
            const request = store.add(alertData);
            
            request.onsuccess = () => resolve();
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    displayAlertOnUI(alertData) {
        // Dispatch event for UI to display alert
        const event = new CustomEvent('postOpAlert', {
            detail: alertData
        });
        document.dispatchEvent(event);
    }
    
    async syncDataWithServer(data) {
        try {
            const response = await fetch('/api/v1/post-op/metrics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify(data),
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Update sync status in local DB
                this.updateSyncStatus(data.id, 'synced');
            } else {
                console.error('Failed to sync data with server:', await response.text());
            }
        } catch (error) {
            console.error('Error syncing data with server:', error);
            this.syncStatus = 'offline';
        }
    }
    
    async syncAlertWithServer(alertData) {
        try {
            const response = await fetch('/api/v1/post-op/alerts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify(alertData),
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                console.error('Failed to sync alert with server:', await response.text());
            }
        } catch (error) {
            console.error('Error syncing alert with server:', error);
        }
    }
    
    async syncOfflineData() {
        if (!this.dbInstance) return;
        
        // Get all pending metrics
        const pendingMetrics = await this.getPendingMetrics();
        
        for (const metric of pendingMetrics) {
            await this.syncDataWithServer(metric);
        }
        
        // Get all pending alerts
        const pendingAlerts = await this.getPendingAlerts();
        
        for (const alert of pendingAlerts) {
            await this.syncAlertWithServer(alert);
        }
        
        console.log(`Synced ${pendingMetrics.length} metrics and ${pendingAlerts.length} alerts`);
    }
    
    async getPendingMetrics() {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['metrics'], 'readonly');
            const store = transaction.objectStore('metrics');
            const index = store.index('by_sync_status');
            const request = index.getAll(IDBKeyRange.only('pending'));
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    async getPendingAlerts() {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['alerts'], 'readonly');
            const store = transaction.objectStore('alerts');
            const index = store.index('by_sync_status');
            const request = index.getAll(IDBKeyRange.only('pending'));
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    async updateSyncStatus(id, status) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['metrics'], 'readwrite');
            const store = transaction.objectStore('metrics');
            
            const getRequest = store.get(id);
            
            getRequest.onsuccess = () => {
                const data = getRequest.result;
                if (data) {
                    data.syncStatus = status;
                    const updateRequest = store.put(data);
                    
                    updateRequest.onsuccess = () => resolve();
                    updateRequest.onerror = (event) => reject(event.target.error);
                } else {
                    reject(new Error('Metric not found'));
                }
            };
            
            getRequest.onerror = (event) => reject(event.target.error);
        });
    }
    
    showOfflineNotification() {
        // Display offline mode indicator in UI
        const event = new CustomEvent('connectionStatusChange', {
            detail: { status: 'offline' }
        });
        document.dispatchEvent(event);
        
        // Show notification if permitted
        if (this.notificationPermission) {
            new Notification('Offline Mode', {
                body: 'You are now working in offline mode. Data will be synced when connection is restored.',
                icon: '/static/img/offline-icon.png'
            });
        }
    }
    
    logAudit(action, details) {
        if (!this.dbInstance) return;
        
        const auditEntry = {
            userId: window.currentUser ? window.currentUser.id : 'unknown',
            action: action,
            details: details,
            timestamp: new Date().toISOString(),
            ipAddress: window.clientIp || 'unknown',
            userAgent: navigator.userAgent,
            syncStatus: 'pending'
        };
        
        const transaction = this.dbInstance.transaction(['audit'], 'readwrite');
        const store = transaction.objectStore('audit');
        store.add(auditEntry);
        
        // If online, also send to server
        if (this.syncStatus === 'online') {
            this.syncAuditWithServer(auditEntry);
        }
    }
    
    async syncAuditWithServer(auditEntry) {
        try {
            await fetch('/api/v1/audit/log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify(auditEntry),
                credentials: 'same-origin'
            });
        } catch (error) {
            console.error('Error syncing audit log with server:', error);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.postOpMonitoring = new PostOpMonitoring();
});

// Export for module use
export default PostOpMonitoring;
