/**
 * PWA Integration Module for Gastric ADCI Platform
 * Orchestrates all PWA features and ensures seamless integration
 */

// Import all PWA modules
import DicomViewer from './pwa/dicom-viewer.js';
import ServiceWorkerManager from './pwa/service-worker.js';
import WebRTCCollaboration from './pwa/webrtc-collab.js';
import ARVisualization from './pwa/ar-visualization.js';
import PostOpMonitoring from './pwa/post-op-monitoring.js';
import AIAnalytics from './pwa/ai-analytics.js';
import InstrumentTracking from './pwa/instrument-tracking.js';

class PWAIntegration {
    constructor() {
        this.modules = {
            serviceWorker: null,
            dicom: null,
            collaboration: null,
            ar: null,
            postOp: null,
            ai: null,
            instruments: null
        };
        this.featureSupport = {};
        this.moduleStatus = {};
        this.preferences = {};
        this.isInitialized = false;
        
        // Initialize immediately
        this.init();
    }
    
    async init() {
        try {
            console.log('Initializing PWA integration module...');
            
            // Check browser feature support
            this.checkBrowserSupport();
            
            // Load user preferences
            await this.loadPreferences();
            
            // Initialize service worker first (core PWA functionality)
            await this.initServiceWorker();
            
            // Initialize the rest of the modules in parallel
            await Promise.all([
                this.initDicomViewer(),
                this.initWebRTCCollaboration(),
                this.initARVisualization(),
                this.initPostOpMonitoring(),
                this.initAIAnalytics(),
                this.initInstrumentTracking()
            ]);
            
            // Register cross-module event handlers
            this.registerEventHandlers();
            
            // Set up UI integration
            this.setupUIIntegration();
            
            this.isInitialized = true;
            console.log('PWA integration complete');
            
            // Dispatch ready event
            document.dispatchEvent(new CustomEvent('pwaReady'));
        } catch (error) {
            console.error('Failed to initialize PWA integration:', error);
            document.dispatchEvent(new CustomEvent('pwaError', {
                detail: { error: error.message }
            }));
        }
    }
    
    checkBrowserSupport() {
        // Check for PWA features support
        this.featureSupport = {
            serviceWorker: 'serviceWorker' in navigator,
            caches: 'caches' in window,
            indexedDB: 'indexedDB' in window,
            webrtc: navigator.mediaDevices && navigator.mediaDevices.getUserMedia && RTCPeerConnection,
            webgl: !!document.createElement('canvas').getContext('webgl2') || 
                  !!document.createElement('canvas').getContext('webgl'),
            webgpu: !!window.navigator.gpu,
            webxr: 'xr' in navigator,
            bluetooth: 'bluetooth' in navigator,
            notifications: 'Notification' in window,
            mediaSession: 'mediaSession' in navigator,
            webShare: 'share' in navigator,
            credentials: 'credentials' in navigator,
            paymentRequest: 'PaymentRequest' in window,
            vibration: 'vibrate' in navigator,
            deviceMotion: !!window.DeviceMotionEvent,
            deviceOrientation: !!window.DeviceOrientationEvent,
            mediaCapabilities: 'mediaCapabilities' in navigator
        };
        
        console.log('Browser feature support:', this.featureSupport);
        
        // Dispatch event with browser support info
        document.dispatchEvent(new CustomEvent('browserSupportChecked', {
            detail: { support: this.featureSupport }
        }));
    }
    
    async loadPreferences() {
        try {
            // Try to load from server first
            const response = await fetch('/api/v1/pwa/preferences', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                this.preferences = await response.json();
                return;
            }
        } catch (error) {
            console.warn('Error loading preferences from server:', error);
        }
        
        // Fallback to local storage
        const storedPrefs = localStorage.getItem('pwaPreferences');
        if (storedPrefs) {
            try {
                this.preferences = JSON.parse(storedPrefs);
            } catch (e) {
                console.error('Error parsing stored preferences:', e);
                this.setDefaultPreferences();
            }
        } else {
            this.setDefaultPreferences();
        }
    }
    
    setDefaultPreferences() {
        // Set default preferences
        this.preferences = {
            modules: {
                serviceWorker: true,
                dicom: true,
                collaboration: true,
                ar: true,
                postOp: true,
                ai: true,
                instruments: true
            },
            offlineMode: {
                enabled: true,
                syncFrequency: 'auto', // 'auto', 'manual', or interval in minutes
                storageLimit: 500 // MB
            },
            performance: {
                highPerformanceMode: false,
                reducedMotion: false,
                dataOptimization: true
            },
            security: {
                biometricAuth: true,
                sessionTimeout: 30, // minutes
                dataEncryption: true
            },
            accessibility: {
                highContrast: false,
                largeText: false,
                screenReader: false
            },
            notifications: {
                enabled: true,
                sound: true,
                vibration: true,
                clinicalAlerts: true,
                systemAlerts: true,
                collaborationAlerts: true
            }
        };
        
        // Save to local storage
        localStorage.setItem('pwaPreferences', JSON.stringify(this.preferences));
    }
    
    async initServiceWorker() {
        if (!this.featureSupport.serviceWorker || !this.preferences.modules.serviceWorker) {
            console.warn('Service Worker not supported or disabled');
            this.moduleStatus.serviceWorker = 'disabled';
            return;
        }
        
        try {
            this.modules.serviceWorker = new ServiceWorkerManager();
            await this.modules.serviceWorker.register();
            this.moduleStatus.serviceWorker = 'active';
            
            // Check for updates
            this.modules.serviceWorker.checkForUpdates();
            
            console.log('Service Worker initialized');
        } catch (error) {
            console.error('Service Worker initialization failed:', error);
            this.moduleStatus.serviceWorker = 'error';
        }
    }
    
    async initDicomViewer() {
        if (!this.featureSupport.webgl || !this.preferences.modules.dicom) {
            console.warn('DICOM Viewer not supported or disabled');
            this.moduleStatus.dicom = 'disabled';
            return;
        }
        
        try {
            this.modules.dicom = new DicomViewer();
            this.moduleStatus.dicom = 'active';
            
            console.log('DICOM Viewer initialized');
        } catch (error) {
            console.error('DICOM Viewer initialization failed:', error);
            this.moduleStatus.dicom = 'error';
        }
    }
    
    async initWebRTCCollaboration() {
        if (!this.featureSupport.webrtc || !this.preferences.modules.collaboration) {
            console.warn('WebRTC Collaboration not supported or disabled');
            this.moduleStatus.collaboration = 'disabled';
            return;
        }
        
        try {
            this.modules.collaboration = new WebRTCCollaboration();
            this.moduleStatus.collaboration = 'active';
            
            console.log('WebRTC Collaboration initialized');
        } catch (error) {
            console.error('WebRTC Collaboration initialization failed:', error);
            this.moduleStatus.collaboration = 'error';
        }
    }
    
    async initARVisualization() {
        if (!this.featureSupport.webxr || !this.preferences.modules.ar) {
            console.warn('AR Visualization not supported or disabled');
            this.moduleStatus.ar = 'disabled';
            return;
        }
        
        try {
            this.modules.ar = new ARVisualization();
            this.moduleStatus.ar = 'active';
            
            console.log('AR Visualization initialized');
        } catch (error) {
            console.error('AR Visualization initialization failed:', error);
            this.moduleStatus.ar = 'error';
        }
    }
    
    async initPostOpMonitoring() {
        if (!this.featureSupport.indexedDB || !this.preferences.modules.postOp) {
            console.warn('Post-Op Monitoring not supported or disabled');
            this.moduleStatus.postOp = 'disabled';
            return;
        }
        
        try {
            this.modules.postOp = new PostOpMonitoring();
            this.moduleStatus.postOp = 'active';
            
            console.log('Post-Op Monitoring initialized');
        } catch (error) {
            console.error('Post-Op Monitoring initialization failed:', error);
            this.moduleStatus.postOp = 'error';
        }
    }
    
    async initAIAnalytics() {
        if (!this.preferences.modules.ai) {
            console.warn('AI Analytics disabled');
            this.moduleStatus.ai = 'disabled';
            return;
        }
        
        try {
            this.modules.ai = new AIAnalytics();
            this.moduleStatus.ai = 'active';
            
            console.log('AI Analytics initialized');
        } catch (error) {
            console.error('AI Analytics initialization failed:', error);
            this.moduleStatus.ai = 'error';
        }
    }
    
    async initInstrumentTracking() {
        if (!this.featureSupport.indexedDB || !this.preferences.modules.instruments) {
            console.warn('Instrument Tracking not supported or disabled');
            this.moduleStatus.instruments = 'disabled';
            return;
        }
        
        try {
            this.modules.instruments = new InstrumentTracking();
            this.moduleStatus.instruments = 'active';
            
            console.log('Instrument Tracking initialized');
        } catch (error) {
            console.error('Instrument Tracking initialization failed:', error);
            this.moduleStatus.instruments = 'error';
        }
    }
    
    registerEventHandlers() {
        // Handle cross-module communication and events
        
        // Service Worker events
        window.addEventListener('online', () => {
            document.dispatchEvent(new CustomEvent('networkStatusChange', {
                detail: { status: 'online' }
            }));
            
            if (this.modules.serviceWorker) {
                this.modules.serviceWorker.syncData();
            }
        });
        
        window.addEventListener('offline', () => {
            document.dispatchEvent(new CustomEvent('networkStatusChange', {
                detail: { status: 'offline' }
            }));
        });
        
        // Connect DICOM viewer with AR visualization
        document.addEventListener('dicomSeriesLoaded', (event) => {
            if (this.modules.ar && this.moduleStatus.ar === 'active') {
                this.modules.ar.importDicomData(event.detail);
            }
        });
        
        // Connect WebRTC with DICOM and AR
        document.addEventListener('collaborationSessionStarted', (event) => {
            // Share DICOM state
            if (this.modules.dicom && this.moduleStatus.dicom === 'active') {
                const dicomState = this.modules.dicom.getState();
                this.modules.collaboration.shareData('dicomState', dicomState);
            }
            
            // Share AR state
            if (this.modules.ar && this.moduleStatus.ar === 'active') {
                const arState = this.modules.ar.getState();
                this.modules.collaboration.shareData('arState', arState);
            }
        });
        
        // Connect AI analytics with post-op monitoring
        document.addEventListener('postOpAlert', (event) => {
            if (this.modules.ai && this.moduleStatus.ai === 'active') {
                // Trigger predictive analysis based on alert
                document.dispatchEvent(new CustomEvent('requestAnalysis', {
                    detail: {
                        analysisType: 'complication-risk',
                        patientData: {
                            id: event.detail.patientId,
                            metricType: event.detail.metricType,
                            metricValue: event.detail.metricValue
                        },
                        options: {
                            priority: 'high',
                            context: 'alert-triggered'
                        }
                    }
                }));
            }
        });
        
        // Connect instrument tracking with AI
        document.addEventListener('caseEnded', (event) => {
            if (this.modules.ai && this.moduleStatus.ai === 'active' && 
                this.modules.instruments && this.moduleStatus.instruments === 'active') {
                // Analyze case data for patterns
                const caseData = this.modules.instruments.activeCase;
                
                if (caseData) {
                    document.dispatchEvent(new CustomEvent('requestAnalysis', {
                        detail: {
                            analysisType: 'protocol-compliance',
                            patientData: {
                                id: caseData.patientId,
                                caseId: caseData.id,
                                procedureType: caseData.procedureType,
                                instruments: caseData.instruments,
                                duration: new Date(caseData.endTime) - new Date(caseData.startTime)
                            },
                            options: {
                                includeTrends: true
                            }
                        }
                    }));
                }
            }
        });
    }
    
    setupUIIntegration() {
        // Initialize UI elements
        this.createStatusIndicator();
        this.createFeatureToggles();
        
        // Register module-specific UI controls
        for (const [moduleName, module] of Object.entries(this.modules)) {
            if (module && this.moduleStatus[moduleName] === 'active') {
                // Add module-specific UI controls
                const containerSelector = `#${moduleName}-container`;
                const container = document.querySelector(containerSelector);
                
                if (container) {
                    this.initModuleUI(moduleName, module, container);
                }
            }
        }
    }
    
    createStatusIndicator() {
        // Create a status indicator in the UI
        const statusContainer = document.createElement('div');
        statusContainer.id = 'pwa-status-indicator';
        statusContainer.className = 'pwa-status-indicator';
        
        // Set initial status
        const statusText = document.createElement('span');
        statusText.textContent = navigator.onLine ? 'Online' : 'Offline';
        statusText.className = navigator.onLine ? 'status-online' : 'status-offline';
        
        statusContainer.appendChild(statusText);
        
        // Add status for each module
        const moduleStatusList = document.createElement('ul');
        moduleStatusList.className = 'module-status-list hidden';
        
        for (const [moduleName, status] of Object.entries(this.moduleStatus)) {
            const listItem = document.createElement('li');
            listItem.textContent = `${this.formatModuleName(moduleName)}: ${status}`;
            listItem.className = `status-${status}`;
            moduleStatusList.appendChild(listItem);
        }
        
        statusContainer.appendChild(moduleStatusList);
        
        // Toggle module status list visibility on click
        statusContainer.addEventListener('click', () => {
            moduleStatusList.classList.toggle('hidden');
        });
        
        // Update status on network change
        window.addEventListener('online', () => {
            statusText.textContent = 'Online';
            statusText.className = 'status-online';
        });
        
        window.addEventListener('offline', () => {
            statusText.textContent = 'Offline';
            statusText.className = 'status-offline';
        });
        
        // Add to document
        document.body.appendChild(statusContainer);
    }
    
    createFeatureToggles() {
        // Create toggles for enabling/disabling features
        const toggleContainer = document.createElement('div');
        toggleContainer.id = 'pwa-feature-toggles';
        toggleContainer.className = 'pwa-feature-toggles hidden';
        
        const toggleHeader = document.createElement('h3');
        toggleHeader.textContent = 'PWA Features';
        toggleContainer.appendChild(toggleHeader);
        
        const toggleList = document.createElement('ul');
        
        for (const [moduleName, enabled] of Object.entries(this.preferences.modules)) {
            const listItem = document.createElement('li');
            
            const label = document.createElement('label');
            label.textContent = this.formatModuleName(moduleName);
            
            const toggle = document.createElement('input');
            toggle.type = 'checkbox';
            toggle.checked = enabled;
            toggle.disabled = moduleName === 'serviceWorker'; // Don't allow disabling core service worker
            
            toggle.addEventListener('change', (event) => {
                this.toggleModule(moduleName, event.target.checked);
            });
            
            label.prepend(toggle);
            listItem.appendChild(label);
            toggleList.appendChild(listItem);
        }
        
        toggleContainer.appendChild(toggleList);
        
        // Add settings button to status indicator
        const statusIndicator = document.getElementById('pwa-status-indicator');
        if (statusIndicator) {
            const settingsButton = document.createElement('button');
            settingsButton.className = 'settings-button';
            settingsButton.textContent = '⚙️';
            settingsButton.setAttribute('aria-label', 'PWA Settings');
            
            settingsButton.addEventListener('click', (event) => {
                event.stopPropagation();
                toggleContainer.classList.toggle('hidden');
            });
            
            statusIndicator.appendChild(settingsButton);
        }
        
        // Add to document
        document.body.appendChild(toggleContainer);
    }
    
    initModuleUI(moduleName, module, container) {
        // Create module-specific UI controls
        switch (moduleName) {
            case 'dicom':
                // DICOM viewer controls would be added here
                break;
                
            case 'collaboration':
                // WebRTC collaboration controls would be added here
                break;
                
            case 'ar':
                // AR visualization controls would be added here
                break;
                
            case 'postOp':
                // Post-op monitoring controls would be added here
                break;
                
            case 'ai':
                // AI analytics controls would be added here
                break;
                
            case 'instruments':
                // Instrument tracking controls would be added here
                break;
        }
    }
    
    async toggleModule(moduleName, enabled) {
        // Update preferences
        this.preferences.modules[moduleName] = enabled;
        
        // Save preferences
        localStorage.setItem('pwaPreferences', JSON.stringify(this.preferences));
        
        // Try to sync with server
        if (navigator.onLine) {
            try {
                await fetch('/api/v1/pwa/preferences', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
                    },
                    body: JSON.stringify(this.preferences),
                    credentials: 'same-origin'
                });
            } catch (error) {
                console.error('Error saving preferences to server:', error);
            }
        }
        
        // Reinitialize or disable module
        if (enabled) {
            // Re-initialize the module
            switch (moduleName) {
                case 'dicom':
                    await this.initDicomViewer();
                    break;
                case 'collaboration':
                    await this.initWebRTCCollaboration();
                    break;
                case 'ar':
                    await this.initARVisualization();
                    break;
                case 'postOp':
                    await this.initPostOpMonitoring();
                    break;
                case 'ai':
                    await this.initAIAnalytics();
                    break;
                case 'instruments':
                    await this.initInstrumentTracking();
                    break;
            }
        } else {
            // Clean up and disable module
            if (this.modules[moduleName]) {
                if (typeof this.modules[moduleName].cleanup === 'function') {
                    await this.modules[moduleName].cleanup();
                }
                
                this.modules[moduleName] = null;
                this.moduleStatus[moduleName] = 'disabled';
            }
        }
        
        // Update status display
        this.updateModuleStatusDisplay();
    }
    
    updateModuleStatusDisplay() {
        const moduleStatusList = document.querySelector('.module-status-list');
        if (!moduleStatusList) return;
        
        // Clear current list
        moduleStatusList.innerHTML = '';
        
        // Rebuild list with current status
        for (const [moduleName, status] of Object.entries(this.moduleStatus)) {
            const listItem = document.createElement('li');
            listItem.textContent = `${this.formatModuleName(moduleName)}: ${status}`;
            listItem.className = `status-${status}`;
            moduleStatusList.appendChild(listItem);
        }
    }
    
    formatModuleName(moduleName) {
        // Convert camelCase to Title Case with spaces
        switch (moduleName) {
            case 'serviceWorker':
                return 'Service Worker';
            case 'dicom':
                return 'DICOM Viewer';
            case 'collaboration':
                return 'Team Collaboration';
            case 'ar':
                return 'AR Visualization';
            case 'postOp':
                return 'Post-Op Monitoring';
            case 'ai':
                return 'AI Analytics';
            case 'instruments':
                return 'Instrument Tracking';
            default:
                return moduleName.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
        }
    }
    
    // Method to get module status for external use
    getModuleStatus() {
        return { ...this.moduleStatus };
    }
    
    // Method to check if specific features are supported
    isFeatureSupported(featureName) {
        return this.featureSupport[featureName] || false;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pwaIntegration = new PWAIntegration();
});

// Export for module use
export default PWAIntegration;
