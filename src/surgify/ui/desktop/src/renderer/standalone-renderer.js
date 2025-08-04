// Standalone Desktop Renderer - No React Dependencies Required
// This provides the same functionality as the React version but using vanilla JavaScript

class DesktopApp {
    constructor() {
        this.state = {
            isLoading: true,
            isOnline: navigator.onLine,
            isAuthenticated: false,
            userInfo: null,
            connectionStatus: 'connecting',
            currentUrl: '',
            securityStatus: 'secure'
        };

        this.webViewManager = new WebViewManager();
        this.authManager = new AuthManager();
        this.connectionManager = new ConnectionManager();

        this.init();
    }

    async init() {
        try {
            // Set up event listeners
            this.setupEventListeners();
            
            // Initialize services
            await this.initializeServices();
            
            // Load the application
            await this.loadApplication();
            
        } catch (error) {
            console.error('App initialization failed:', error);
            this.setState({
                isLoading: false,
                connectionStatus: 'error',
                securityStatus: 'error'
            });
        }
    }

    setupEventListeners() {
        // Window controls
        const closeBtn = document.getElementById('close-btn');
        const minimizeBtn = document.getElementById('minimize-btn');
        const maximizeBtn = document.getElementById('maximize-btn');
        const retryBtn = document.getElementById('retry-btn');

        if (closeBtn) closeBtn.addEventListener('click', () => this.handleWindowControl('close'));
        if (minimizeBtn) minimizeBtn.addEventListener('click', () => this.handleWindowControl('minimize'));
        if (maximizeBtn) maximizeBtn.addEventListener('click', () => this.handleWindowControl('maximize'));
        if (retryBtn) retryBtn.addEventListener('click', () => this.handleRetryConnection());

        // Online/offline detection
        window.addEventListener('online', () => this.handleOnlineStatusChange());
        window.addEventListener('offline', () => this.handleOnlineStatusChange());

        // Service event listeners
        this.connectionManager.onStatusChange((status) => this.handleConnectionChange(status));
        this.authManager.onAuthChange((isAuth, userInfo) => this.handleAuthChange(isAuth, userInfo));
        this.webViewManager.onUrlChange((url) => this.handleUrlChange(url));
        this.webViewManager.onSecurityStatusChange((status) => this.handleSecurityStatusChange(status));
    }

    async initializeServices() {
        await this.webViewManager.initialize();
        await this.authManager.initialize();
        await this.connectionManager.initialize();
    }

    async loadApplication() {
        // Check authentication status
        const authStatus = await this.authManager.checkAuthStatus();
        this.handleAuthChange(authStatus.isAuthenticated, authStatus.userInfo);

        // Load the main application
        await this.webViewManager.loadUrl('https://surgify.com/workstation');
    }

    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.render();
    }

    handleWindowControl(action) {
        if (window.electronAPI?.windowControl) {
            window.electronAPI.windowControl(action);
        }
    }

    handleConnectionChange(status) {
        this.setState({ connectionStatus: status });
    }

    handleAuthChange(isAuthenticated, userInfo) {
        this.setState({ 
            isAuthenticated, 
            userInfo,
            isLoading: false 
        });
    }

    handleOnlineStatusChange() {
        const isOnline = navigator.onLine;
        this.setState({ isOnline });
        
        if (isOnline) {
            this.connectionManager.reconnect();
        }
    }

    handleUrlChange(url) {
        this.setState({ currentUrl: url });
    }

    handleSecurityStatusChange(status) {
        this.setState({ securityStatus: status });
    }

    async handleRetryConnection() {
        this.setState({ connectionStatus: 'connecting' });
        try {
            await this.connectionManager.reconnect();
            await this.webViewManager.reload();
        } catch (error) {
            console.error('Reconnection failed:', error);
            this.setState({ connectionStatus: 'error' });
        }
    }

    render() {
        this.updateLoadingScreen();
        this.updateOfflineScreen();
        this.updateWebViewContainer();
        this.updateStatusBar();
    }

    updateLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (!loadingScreen) return;

        if (this.state.isLoading) {
            loadingScreen.classList.remove('hidden');
        } else {
            loadingScreen.classList.add('hidden');
        }
    }

    updateOfflineScreen() {
        const offlineMessage = document.getElementById('offline-message');
        if (!offlineMessage) return;

        if (!this.state.isOnline && !this.state.isLoading) {
            offlineMessage.classList.remove('hidden');
        } else {
            offlineMessage.classList.add('hidden');
        }
    }

    updateWebViewContainer() {
        const webviewContainer = document.querySelector('.webview-container');
        if (!webviewContainer) return;

        if (!this.state.isLoading && this.state.isOnline) {
            webviewContainer.style.opacity = '1';
        } else {
            webviewContainer.style.opacity = '0.5';
        }
    }

    updateStatusBar() {
        this.updateConnectionStatus();
        this.updateUserInfo();
        this.updateSecurityStatus();
    }

    updateConnectionStatus() {
        const connectionStatus = document.getElementById('connection-status');
        const connectionText = document.getElementById('connection-text');
        
        if (connectionStatus && connectionText) {
            // Update status dot
            connectionStatus.className = 'status-dot';
            switch (this.state.connectionStatus) {
                case 'connected':
                    connectionStatus.classList.add('connected');
                    connectionText.textContent = 'Connected';
                    break;
                case 'connecting':
                    connectionStatus.classList.add('warning');
                    connectionText.textContent = 'Connecting...';
                    break;
                case 'disconnected':
                case 'error':
                    connectionStatus.classList.add('error');
                    connectionText.textContent = this.state.connectionStatus === 'error' ? 'Connection Error' : 'Disconnected';
                    break;
            }
        }
    }

    updateUserInfo() {
        const userInfo = document.getElementById('user-info');
        if (!userInfo) return;

        if (this.state.isAuthenticated && this.state.userInfo) {
            userInfo.textContent = `${this.state.userInfo.name} (${this.state.userInfo.role})`;
        } else {
            userInfo.textContent = 'Not logged in';
        }
    }

    updateSecurityStatus() {
        const securityStatus = document.getElementById('security-status');
        if (!securityStatus) return;

        switch (this.state.securityStatus) {
            case 'secure':
                securityStatus.textContent = 'Secure';
                securityStatus.className = 'secure';
                break;
            case 'warning':
                securityStatus.textContent = 'Warning';
                securityStatus.className = 'warning';
                break;
            case 'error':
                securityStatus.textContent = 'Insecure';
                securityStatus.className = 'error';
                break;
        }
    }
}

// Service Classes (Vanilla JavaScript versions)

class AuthManager {
    constructor() {
        this.listeners = [];
        this.currentAuthStatus = {
            isAuthenticated: false,
            userInfo: null
        };
    }

    async initialize() {
        try {
            const token = await window.electronAPI?.getAuthToken?.();
            if (token) {
                const userInfo = await this.validateToken(token);
                if (userInfo) {
                    this.currentAuthStatus = {
                        isAuthenticated: true,
                        userInfo,
                        token
                    };
                }
            }
        } catch (error) {
            console.error('Auth initialization failed:', error);
        }
    }

    async checkAuthStatus() {
        return this.currentAuthStatus;
    }

    async validateToken(token) {
        try {
            const response = await fetch('https://api.surgify.com/auth/validate', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data.user;
            }
            return null;
        } catch (error) {
            console.error('Token validation failed:', error);
            return null;
        }
    }

    onAuthChange(callback) {
        this.listeners.push(callback);
    }

    notifyListeners(isAuthenticated, userInfo) {
        this.listeners.forEach(callback => callback(isAuthenticated, userInfo));
    }
}

class ConnectionManager {
    constructor() {
        this.listeners = [];
        this.currentStatus = { status: 'disconnected' };
        this.reconnectInterval = null;
        this.healthCheckInterval = null;
    }

    async initialize() {
        this.startHealthCheck();
        
        if (window.electronAPI?.onNetworkChange) {
            window.electronAPI.onNetworkChange((isOnline) => {
                if (isOnline) {
                    this.reconnect();
                } else {
                    this.setStatus('disconnected');
                }
            });
        }

        await this.connect();
    }

    async connect() {
        this.setStatus('connecting');
        
        try {
            const isOnline = await window.electronAPI?.isOnline?.() ?? navigator.onLine;
            
            if (!isOnline) {
                this.setStatus('disconnected');
                return;
            }

            const startTime = Date.now();
            const response = await fetch('https://api.surgify.com/health', {
                method: 'GET'
            });

            if (response.ok) {
                const latency = Date.now() - startTime;
                this.currentStatus = {
                    status: 'connected',
                    lastConnected: new Date(),
                    latency
                };
                this.setStatus('connected');
            } else {
                throw new Error('Health check failed');
            }
        } catch (error) {
            console.error('Connection failed:', error);
            this.setStatus('error');
        }
    }

    async reconnect() {
        if (this.reconnectInterval) {
            clearInterval(this.reconnectInterval);
            this.reconnectInterval = null;
        }

        await this.connect();

        if (this.currentStatus.status !== 'connected') {
            this.scheduleReconnect();
        }
    }

    scheduleReconnect() {
        if (this.reconnectInterval) return;

        this.reconnectInterval = setInterval(async () => {
            await this.connect();
            
            if (this.currentStatus.status === 'connected') {
                clearInterval(this.reconnectInterval);
                this.reconnectInterval = null;
            }
        }, 10000);
    }

    startHealthCheck() {
        this.healthCheckInterval = setInterval(async () => {
            if (this.currentStatus.status === 'connected') {
                try {
                    const startTime = Date.now();
                    const response = await fetch('https://api.surgify.com/health', {
                        method: 'GET'
                    });

                    if (response.ok) {
                        const latency = Date.now() - startTime;
                        this.currentStatus.latency = latency;
                    } else {
                        throw new Error('Health check failed');
                    }
                } catch (error) {
                    console.error('Health check failed:', error);
                    this.setStatus('error');
                    this.scheduleReconnect();
                }
            }
        }, 30000);
    }

    onStatusChange(callback) {
        this.listeners.push(callback);
    }

    setStatus(status) {
        this.currentStatus.status = status;
        this.listeners.forEach(callback => callback(status));
    }
}

class WebViewManager {
    constructor() {
        this.webview = null;
        this.urlChangeListeners = [];
        this.securityStatusListeners = [];
        this.currentSecurityStatus = {
            status: 'secure',
            certificateValid: true,
            connectionSecure: true,
            lastCheck: new Date()
        };
    }

    async initialize() {
        this.webview = document.getElementById('webview');
        
        if (!this.webview) {
            throw new Error('WebView element not found');
        }

        this.setupEventListeners();
    }

    setupEventListeners() {
        if (!this.webview) return;

        this.webview.addEventListener('did-navigate', (event) => {
            this.notifyUrlChange(event.url);
            this.checkSecurityStatus(event.url);
        });

        this.webview.addEventListener('did-navigate-in-page', (event) => {
            this.notifyUrlChange(event.url);
        });

        this.webview.addEventListener('did-fail-load', (event) => {
            console.error('WebView failed to load:', event.errorDescription);
            this.updateSecurityStatus('error');
        });

        this.webview.addEventListener('certificate-error', (event) => {
            console.error('Certificate error:', event);
            this.updateSecurityStatus('error');
        });
    }

    async loadUrl(url) {
        if (!this.webview) {
            throw new Error('WebView not initialized');
        }

        if (!this.isUrlTrusted(url)) {
            throw new Error('Untrusted URL blocked');
        }

        this.webview.src = url;
        await this.checkSecurityStatus(url);
    }

    async reload() {
        if (!this.webview) return;
        this.webview.reload();
    }

    isUrlTrusted(url) {
        const trustedDomains = [
            'https://surgify.com',
            'https://api.surgify.com',
            'https://app.surgify.com',
            'https://secure.surgify.com'
        ];

        return trustedDomains.some(domain => url.startsWith(domain));
    }

    async checkSecurityStatus(url) {
        try {
            const certificateValid = await window.electronAPI?.validateCertificate?.(url) ?? true;
            const connectionSecure = url.startsWith('https://');
            
            let status = 'secure';
            
            if (!certificateValid) {
                status = 'error';
            } else if (!connectionSecure) {
                status = 'warning';
            }

            this.currentSecurityStatus = {
                status,
                certificateValid,
                connectionSecure,
                lastCheck: new Date()
            };

            this.notifySecurityStatusChange(status);
        } catch (error) {
            console.error('Security check failed:', error);
            this.updateSecurityStatus('error');
        }
    }

    updateSecurityStatus(status) {
        this.currentSecurityStatus.status = status;
        this.currentSecurityStatus.lastCheck = new Date();
        this.notifySecurityStatusChange(status);
    }

    onUrlChange(callback) {
        this.urlChangeListeners.push(callback);
    }

    onSecurityStatusChange(callback) {
        this.securityStatusListeners.push(callback);
    }

    notifyUrlChange(url) {
        this.urlChangeListeners.forEach(callback => callback(url));
    }

    notifySecurityStatusChange(status) {
        this.securityStatusListeners.forEach(callback => callback(status));
    }
}

// Initialize the application when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new DesktopApp();
});
