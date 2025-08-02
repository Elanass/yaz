// Base JavaScript for Gastric ADCI Platform - Multi-Environment Support

class GastricADCIApp {
    constructor() {
        this.config = window.APP_CONFIG || {};
        this.apiBase = this.config.apiBaseUrl || '/api/v1';
        this.environment = this.config.environment || 'local';
        this.p2pEnabled = this.config.p2pEnabled || false;
        this.cloudProvider = this.config.cloudProvider || 'none';
        this.features = this.config.features || {};
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeEnvironment();
        this.setupOfflineHandling();
        this.setupP2PIfEnabled();
        this.startStatusMonitoring();
    }

    initializeEnvironment() {
        console.log(`🏥 Gastric ADCI Platform initialized in ${this.environment} mode`);
        
        // Update UI based on environment
        this.updateEnvironmentDisplay();
        
        // Setup environment-specific features
        if (this.environment === 'p2p') {
            this.setupP2PSync();
        } else if (this.environment === 'multicloud') {
            this.setupCloudSync();
        }
    }

    updateEnvironmentDisplay() {
        const statusEl = document.getElementById('sync-status');
        const connectionEl = document.getElementById('connection-status');
        
        if (statusEl) {
            statusEl.textContent = this.getEnvironmentDisplayName();
        }
        
        if (connectionEl) {
            connectionEl.className = 'status-indicator';
            connectionEl.style.color = this.getEnvironmentColor();
        }
    }

    getEnvironmentDisplayName() {
        switch (this.environment) {
            case 'local': return 'Local';
            case 'p2p': return 'P2P Network';
            case 'multicloud': return `Cloud (${this.cloudProvider})`;
            default: return 'Unknown';
        }
    }

    getEnvironmentColor() {
        switch (this.environment) {
            case 'local': return 'var(--env-local)';
            case 'p2p': return 'var(--env-p2p)';
            case 'multicloud': return 'var(--env-cloud)';
            default: return 'var(--text-secondary)';
        }
    }
