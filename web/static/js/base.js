/**
 * Modern Gastric ADCI Platform Base Application
 * Refactored using state-of-the-art patterns and unified utilities
 */

class GastricADCIApp {
    constructor() {
        // Use unified configuration
        this.config = window.APP_CONFIG || {};
        this.apiBase = this.config.apiBaseUrl || '/api/v1';
        this.environment = this.config.environment || 'local';
        this.features = this.config.features || {};
        
        // Use unified HTTP client
        this.http = UnifiedUtils.http;
        
        // Use state management
        this.state = new UnifiedUtils.StateManager({
            user: null,
            environment: this.environment,
            connectionStatus: 'disconnected',
            components: {}
        });
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeEnvironment();
        this.setupOfflineHandling();
        this.startStatusMonitoring();
        
        // Subscribe to state changes
        this.state.subscribe('user', (user) => this.updateUserStatus(user));
        this.state.subscribe('connectionStatus', (status) => this.updateConnectionStatus(status));
    }

    initializeEnvironment() {
        console.log(`🏥 Gastric ADCI Platform initialized in ${this.environment} mode`);
        
        // Update UI based on environment
        this.updateEnvironmentDisplay();
        
        // Setup environment-specific features
        this.setupEnvironmentFeatures();
    }
    
    setupEnvironmentFeatures() {
        const environmentStrategies = {
            p2p: () => this.setupP2PSync(),
            multicloud: () => this.setupCloudSync(),
            local: () => this.setupLocalFeatures()
        };
        
        const strategy = environmentStrategies[this.environment];
        if (strategy) strategy();
    }

    updateEnvironmentDisplay() {
        const statusEl = UnifiedUtils.DOMUtils.query('#sync-status');
        const connectionEl = UnifiedUtils.DOMUtils.query('#connection-status');
        
        if (statusEl) {
            statusEl.textContent = this.getEnvironmentDisplayName();
        }
        
        if (connectionEl) {
            connectionEl.className = 'status-indicator';
            connectionEl.style.color = this.getEnvironmentColor();
        }
    }

    getEnvironmentDisplayName() {
        const names = {
            local: 'Local',
            p2p: 'P2P Network',
            multicloud: `Cloud (${this.config.cloudProvider || 'Generic'})`
        };
        return names[this.environment] || 'Unknown';
    }

    getEnvironmentColor() {
        const colors = {
            local: 'var(--env-local)',
            p2p: 'var(--env-p2p)',
            multicloud: 'var(--env-cloud)'
        };
        return colors[this.environment] || 'var(--text-secondary)';
    }

    setupEventListeners() {
        // Use unified DOM utilities for event delegation
        UnifiedUtils.DOMUtils.delegate(document, '.ajax-form', 'submit', (e) => {
            e.preventDefault();
            this.handleFormSubmission(e.target);
        });

        UnifiedUtils.DOMUtils.delegate(document, '.load-content', 'click', (e) => {
            e.preventDefault();
            this.loadContent(e.target.href, e.target.dataset.target);
        });

        UnifiedUtils.DOMUtils.delegate(document, '.notification-close', 'click', (e) => {
            e.target.closest('.notification').remove();
        });
    }

    async checkUserStatus() {
        try {
            const response = await this.http.get('/auth/me');
            const data = await response.json();
            
            if (response.ok) {
                this.state.setState({ user: data.user });
            }
        } catch (error) {
            console.log('User not authenticated');
            this.state.setState({ user: null });
        }
    }

    updateUserStatus(user) {
        const userEl = UnifiedUtils.DOMUtils.query('#user-status');
        if (userEl) {
            userEl.textContent = user ? `Welcome, ${user.username || user.id}` : 'Not authenticated';
        }
    }

    async handleFormSubmission(form) {
        const validator = this.createFormValidator(form);
        const command = new UnifiedUtils.FormCommand(form, validator);
        
        const result = await command.execute();
        
        if (result.success) {
            UnifiedUtils.notifications.show('Form submitted successfully!', 'success');
            this.handleFormSuccess(result.data, form);
        } else {
            UnifiedUtils.notifications.show('Form submission failed', 'error');
        }
    }
    
    createFormValidator(form) {
        // Create validation rules based on form inputs
        const validator = {};
        
        UnifiedUtils.DOMUtils.queryAll('input[required]', form).forEach(input => {
            const rules = new UnifiedUtils.ValidationComposite()
                .addRule(UnifiedUtils.ValidationRules.required());
            
            if (input.type === 'email') {
                rules.addRule(UnifiedUtils.ValidationRules.email());
            }
            
            validator[input.name] = rules;
        });
        
        return validator;
    }

    handleFormSuccess(data, form) {
        // Handle successful form submission
        if (data.redirect) {
            window.location.href = data.redirect;
        } else if (data.reload) {
            window.location.reload();
        }
    }

    // Environment-specific setup methods
    setupP2PSync() {
        console.log('🔗 Setting up P2P synchronization...');
        // P2P setup logic
    }

    setupCloudSync() {
        console.log('☁️ Setting up cloud synchronization...');
        // Cloud setup logic
    }
    
    setupLocalFeatures() {
        console.log('💻 Setting up local features...');
        // Local features setup
    }

    setupOfflineHandling() {
        window.addEventListener('online', () => {
            this.state.setState({ connectionStatus: 'online' });
            UnifiedUtils.notifications.show('Connection restored', 'success');
        });

        window.addEventListener('offline', () => {
            this.state.setState({ connectionStatus: 'offline' });
            UnifiedUtils.notifications.show('Connection lost - working offline', 'warning');
        });
    }

    startStatusMonitoring() {
        setInterval(() => this.checkSystemHealth(), 30000);
        this.checkUserStatus();
    }

    async checkSystemHealth() {
        try {
            const response = await this.http.get('/health');
            const data = await response.json();
            
            if (response.ok) {
                this.state.setState({ 
                    connectionStatus: 'connected',
                    components: data.components || {}
                });
            }
        } catch (error) {
            this.state.setState({ connectionStatus: 'disconnected' });
        }
    }

    updateConnectionStatus(status) {
        const statusEl = UnifiedUtils.DOMUtils.query('#connection-status');
        if (statusEl) {
            statusEl.className = `status-indicator ${status}`;
            statusEl.textContent = status;
        }
    }

    async loadContent(url, target) {
        const targetEl = UnifiedUtils.DOMUtils.query(target);
        if (!targetEl) return;

        try {
            const response = await this.http.get(url);
            const content = await response.text();
            targetEl.innerHTML = content;
        } catch (error) {
            UnifiedUtils.notifications.show('Failed to load content', 'error');
        }
    }

    // Data sharing using unified patterns
    async shareData(data, type = 'case') {
        const strategies = {
            p2p: () => this.shareViaPeers(data, type),
            multicloud: () => this.shareViaCloud(data, type),
            local: () => this.saveToLocal(data, type)
        };
        
        const strategy = strategies[this.environment];
        if (strategy) return await strategy();
    }

    async shareViaPeers(data, type) {
        // P2P sharing implementation
        console.log('Sharing via P2P:', { data, type });
    }

    async shareViaCloud(data, type) {
        // Cloud sharing implementation
        return await this.http.post(`/sync/${type}`, data);
    }

    saveToLocal(data, type) {
        // Local storage implementation
        localStorage.setItem(`${type}_${Date.now()}`, JSON.stringify(data));
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Ensure unified utilities are loaded first
    if (typeof UnifiedUtils !== 'undefined') {
        window.gastricApp = new GastricADCIApp();
    } else {
        console.error('UnifiedUtils not loaded. Please ensure unified-utils.js is loaded first.');
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GastricADCIApp;
}
