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

    setupEventListeners() {
        // Global form handling
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('ajax-form')) {
                e.preventDefault();
                this.handleFormSubmission(e.target);
            }
        });

        // Global click handling for dynamic actions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('load-content')) {
                e.preventDefault();
                this.loadContent(e.target.href, e.target.dataset.target);
            }
            
            if (e.target.classList.contains('notification-close')) {
                e.target.closest('.notification').remove();
            }
        });

        // Handle environment switching (if enabled)
        if (this.features.environmentSwitching) {
            this.setupEnvironmentSwitching();
        }
    }

    async checkUserStatus() {
        try {
            const response = await fetch(`${this.apiBase}/auth/status`);
            if (response.ok) {
                const user = await response.json();
                this.updateUserStatus(user);
            } else {
                this.updateUserStatus(null);
            }
        } catch (error) {
            console.warn('Could not check user status:', error);
            this.updateUserStatus(null);
        }
    }

    updateUserStatus(user) {
        const userStatusEl = document.getElementById('user-status');
        if (!userStatusEl) return;

        if (user && user.id) {
            userStatusEl.innerHTML = `
                <div class="user-info">
                    <span>Welcome, ${user.name || 'User'}</span>
                    <a href="/auth/logout" class="btn btn-sm btn-outline">Logout</a>
                </div>
            `;
        } else {
            userStatusEl.innerHTML = `
                <div class="auth-links">
                    <a href="/auth/login" class="btn btn-sm btn-primary">Login</a>
                    <a href="/auth/register" class="btn btn-sm btn-outline">Register</a>
                </div>
            `;
        }
    }

    async handleFormSubmission(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Show loading state
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading"></span> Submitting...';
        }

        try {
            const response = await fetch(form.action, {
                method: form.method || 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.showNotification('Success!', 'success');
                
                // Handle redirect if specified
                if (result.redirect) {
                    window.location.href = result.redirect;
                }
            } else {
                throw new Error('Form submission failed');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.showNotification('An error occurred. Please try again.', 'error');
        } finally {
            // Reset button state
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.dataset.originalText || 'Submit';
            }
        }
    }

    // Multi-Environment Support Methods
    setupP2PIfEnabled() {
        if (this.p2pEnabled) {
            console.log('🔗 Initializing P2P networking...');
            this.initP2PConnection();
        }
    }

    setupP2PSync() {
        // P2P sync setup for decentralized collaboration
        if (typeof GUN !== 'undefined') {
            this.gun = GUN(['http://localhost:8765/gun']);
            this.setupP2PDataSync();
        } else {
            console.warn('P2P mode enabled but GUN.js not loaded');
        }
    }

    setupP2PDataSync() {
        // Setup real-time data synchronization
        this.gun.get('adci-platform').on((data, key) => {
            if (data && data.type === 'case-update') {
                this.handleP2PCaseUpdate(data);
            } else if (data && data.type === 'decision-update') {
                this.handleP2PDecisionUpdate(data);
            }
        });
        
        this.updateP2PStatus('connected');
    }

    updateP2PStatus(status) {
        const p2pStatusEl = document.getElementById('p2p-status');
        if (p2pStatusEl) {
            switch (status) {
                case 'connected':
                    p2pStatusEl.textContent = 'P2P: Connected';
                    p2pStatusEl.style.backgroundColor = 'var(--success-color)';
                    break;
                case 'connecting':
                    p2pStatusEl.textContent = 'P2P: Connecting...';
                    p2pStatusEl.style.backgroundColor = 'var(--warning-color)';
                    break;
                case 'disconnected':
                    p2pStatusEl.textContent = 'P2P: Disconnected';
                    p2pStatusEl.style.backgroundColor = 'var(--error-color)';
                    break;
            }
        }
    }

    setupCloudSync() {
        // Cloud synchronization setup
        console.log(`☁️ Setting up cloud sync with ${this.cloudProvider}`);
        
        // Setup cloud-specific configurations
        switch (this.cloudProvider) {
            case 'aws':
                this.setupAWSSync();
                break;
            case 'gcp':
                this.setupGCPSync();
                break;
            case 'azure':
                this.setupAzureSync();
                break;
            default:
                console.warn('Unknown cloud provider:', this.cloudProvider);
        }
    }

    setupAWSSync() {
        // AWS-specific sync configuration
        console.log('📡 Configuring AWS sync...');
    }

    setupGCPSync() {
        // GCP-specific sync configuration
        console.log('📡 Configuring GCP sync...');
    }

    setupAzureSync() {
        // Azure-specific sync configuration
        console.log('📡 Configuring Azure sync...');
    }

    startStatusMonitoring() {
        // Monitor system status and connectivity
        setInterval(() => {
            this.checkSystemHealth();
        }, 30000); // Check every 30 seconds
        
        // Initial check
        this.checkSystemHealth();
    }

    async checkSystemHealth() {
        try {
            const response = await fetch('/health');
            const health = await response.json();
            
            this.updateConnectionStatus(response.ok ? 'connected' : 'error');
            
            if (health.data && health.data.components) {
                this.updateComponentStatus(health.data.components);
            }
        } catch (error) {
            this.updateConnectionStatus('disconnected');
        }
    }

    updateConnectionStatus(status) {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = `status-indicator ${status}`;
        }
    }

    updateComponentStatus(components) {
        // Update individual component statuses
        Object.entries(components).forEach(([component, status]) => {
            const el = document.getElementById(`${component}-status`);
            if (el) {
                el.className = `component-status ${status}`;
                el.textContent = status;
            }
        });
    }

    // Data Collaboration Methods
    async shareData(data, type = 'case') {
        if (this.environment === 'p2p' && this.gun) {
            // Share via P2P network
            this.gun.get('adci-platform').put({
                type: `${type}-update`,
                data: data,
                timestamp: Date.now(),
                source: this.getUserId()
            });
        } else if (this.environment === 'multicloud') {
            // Share via cloud sync
            await this.syncToCloud(data, type);
        } else {
            // Local storage for local environment
            this.saveToLocal(data, type);
        }
    }

    async syncToCloud(data, type) {
        try {
            const response = await fetch(`${this.apiBase}/sync/${type}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.showNotification('Data synced to cloud', 'success');
            }
        } catch (error) {
            console.error('Cloud sync failed:', error);
            this.showNotification('Cloud sync failed', 'error');
        }
    }

    saveToLocal(data, type) {
        const key = `adci-${type}-${Date.now()}`;
        localStorage.setItem(key, JSON.stringify(data));
    }

    getUserId() {
        // Get current user ID from session or generate temp ID
        return localStorage.getItem('userId') || `user-${Date.now()}`;
    }

    // Notification System
    showNotification(message, type = 'info', duration = 5000) {
        const notificationsContainer = document.getElementById('notifications');
        if (!notificationsContainer) return;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button class="notification-close" type="button">×</button>
        `;

        notificationsContainer.appendChild(notification);

        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }

    // Deployment and Configuration Methods
    async loadEnvironmentConfig() {
        try {
            const response = await fetch('/api/v1/config/environment');
            const config = await response.json();
            
            if (config.success) {
                this.updateConfig(config.data);
            }
        } catch (error) {
            console.warn('Could not load environment config:', error);
        }
    }

    updateConfig(newConfig) {
        Object.assign(this.config, newConfig);
        this.apiBase = this.config.apiBaseUrl || this.apiBase;
        this.updateEnvironmentDisplay();
    }

    // Loading and Content Management
    showLoading(text = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        const loadingText = overlay?.querySelector('.loading-text');
        
        if (overlay) {
            if (loadingText) loadingText.textContent = text;
            overlay.style.display = 'flex';
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    async loadContent(url, targetSelector = '#dynamic-content') {
        const target = document.querySelector(targetSelector);
        if (!target) return;

        this.showLoading();

        try {
            const response = await fetch(url);
            const content = await response.text();
            target.innerHTML = content;
            
            // Trigger custom event for content loaded
            target.dispatchEvent(new CustomEvent('contentLoaded', { 
                detail: { url, content } 
            }));
        } catch (error) {
            console.error('Failed to load content:', error);
            this.showNotification('Failed to load content', 'error');
        } finally {
            this.hideLoading();
        }
    }
}

}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.gastricApp = new GastricADCIApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GastricADCIApp;
}
