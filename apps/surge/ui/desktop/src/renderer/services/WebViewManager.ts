import { SecurityStatus } from '../types/global';

export class WebViewManager {
    private webview: Electron.WebviewTag | null = null;
    private urlChangeListeners: Array<(url: string) => void> = [];
    private securityStatusListeners: Array<(status: SecurityStatus['status']) => void> = [];
    private currentSecurityStatus: SecurityStatus = {
        status: 'secure',
        certificateValid: true,
        connectionSecure: true,
        lastCheck: new Date()
    };

    async initialize(): Promise<void> {
        this.webview = document.getElementById('webview') as Electron.WebviewTag;
        
        if (!this.webview) {
            throw new Error('WebView element not found');
        }

        this.setupEventListeners();
    }

    private setupEventListeners(): void {
        if (!this.webview) return;

        // Handle navigation events
        this.webview.addEventListener('did-navigate', (event) => {
            this.notifyUrlChange(event.url);
            this.checkSecurityStatus(event.url);
        });

        this.webview.addEventListener('did-navigate-in-page', (event) => {
            this.notifyUrlChange(event.url);
        });

        // Handle loading events
        this.webview.addEventListener('did-start-loading', () => {
            console.log('WebView started loading');
        });

        this.webview.addEventListener('did-stop-loading', () => {
            console.log('WebView finished loading');
        });

        // Handle security events
        this.webview.addEventListener('did-fail-load', (event) => {
            console.error('WebView failed to load:', event.errorDescription);
            this.updateSecurityStatus('error');
        });

        // Handle certificate errors
        this.webview.addEventListener('certificate-error', (event) => {
            console.error('Certificate error:', event);
            this.updateSecurityStatus('error');
        });

        // Handle console messages from the webview
        this.webview.addEventListener('console-message', (event) => {
            console.log(`WebView console (${event.level}):`, event.message);
        });

        // Handle permission requests
        this.webview.addEventListener('permission-request', (event) => {
            // Allow specific permissions for Surgify functionality
            if (event.permission === 'camera' || 
                event.permission === 'microphone' || 
                event.permission === 'notifications') {
                event.request.allow();
            } else {
                event.request.deny();
            }
        });

        // Handle new window requests
        this.webview.addEventListener('new-window', (event) => {
            // Prevent new windows, open in system browser instead
            event.preventDefault();
            if (event.url.startsWith('https://surgify.com') || 
                event.url.startsWith('https://api.surgify.com')) {
                this.loadUrl(event.url);
            } else {
                // Open external links in system browser
                window.electronAPI?.openExternal?.(event.url);
            }
        });
    }

    async loadUrl(url: string): Promise<void> {
        if (!this.webview) {
            throw new Error('WebView not initialized');
        }

        // Validate URL is from trusted domain
        if (!this.isUrlTrusted(url)) {
            throw new Error('Untrusted URL blocked');
        }

        this.webview.src = url;
        await this.checkSecurityStatus(url);
    }

    async reload(): Promise<void> {
        if (!this.webview) return;
        this.webview.reload();
    }

    async goBack(): Promise<void> {
        if (!this.webview) return;
        if (this.webview.canGoBack()) {
            this.webview.goBack();
        }
    }

    async goForward(): Promise<void> {
        if (!this.webview) return;
        if (this.webview.canGoForward()) {
            this.webview.goForward();
        }
    }

    getCurrentUrl(): string {
        return this.webview?.src || '';
    }

    private isUrlTrusted(url: string): boolean {
        const trustedDomains = [
            'https://surgify.com',
            'https://api.surgify.com',
            'https://app.surgify.com',
            'https://secure.surgify.com'
        ];

        return trustedDomains.some(domain => url.startsWith(domain));
    }

    private async checkSecurityStatus(url: string): Promise<void> {
        try {
            const certificateValid = await window.electronAPI?.validateCertificate(url) ?? true;
            const connectionSecure = url.startsWith('https://');
            
            let status: SecurityStatus['status'] = 'secure';
            
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

    private updateSecurityStatus(status: SecurityStatus['status']): void {
        this.currentSecurityStatus.status = status;
        this.currentSecurityStatus.lastCheck = new Date();
        this.notifySecurityStatusChange(status);
    }

    onUrlChange(callback: (url: string) => void): void {
        this.urlChangeListeners.push(callback);
    }

    onSecurityStatusChange(callback: (status: SecurityStatus['status']) => void): void {
        this.securityStatusListeners.push(callback);
    }

    private notifyUrlChange(url: string): void {
        this.urlChangeListeners.forEach(callback => callback(url));
    }

    private notifySecurityStatusChange(status: SecurityStatus['status']): void {
        this.securityStatusListeners.forEach(callback => callback(status));
    }

    getSecurityStatus(): SecurityStatus {
        return this.currentSecurityStatus;
    }
}
