/**
 * WebAuthn Authentication Component
 * Provides passwordless authentication using Web Authentication API
 */

class WebAuthnAuth {
    constructor() {
        this.isSupported = this.checkSupport();
        this.credentials = new Map();
        this.init();
    }

    checkSupport() {
        return !!(navigator.credentials && 
                  window.PublicKeyCredential && 
                  typeof window.PublicKeyCredential === "function" &&
                  window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable);
    }

    async init() {
        if (!this.isSupported) {
            console.warn('WebAuthn is not supported on this device');
            return;
        }

        // Initialize event listeners
        this.bindEvents();
        
        // Check for existing credentials
        await this.checkExistingCredentials();
    }

    bindEvents() {
        const loginBtn = document.getElementById('login-btn');
        const registerBtn = document.getElementById('register-webauthn');
        const biometricLoginBtn = document.getElementById('biometric-login');

        if (loginBtn) {
            loginBtn.addEventListener('click', () => this.handleTraditionalLogin());
        }

        if (registerBtn) {
            registerBtn.addEventListener('click', () => this.register());
        }

        if (biometricLoginBtn) {
            biometricLoginBtn.addEventListener('click', () => this.authenticate());
        }
    }

    async checkExistingCredentials() {
        try {
            const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
            if (available) {
                this.showBiometricOption();
            }
        } catch (error) {
            console.error('Error checking authenticator availability:', error);
        }
    }

    showBiometricOption() {
        const biometricSection = document.getElementById('biometric-auth-section');
        if (biometricSection) {
            biometricSection.classList.remove('hidden');
        }
    }

    async register() {
        if (!this.isSupported) {
            this.showError('WebAuthn is not supported on this device');
            return;
        }

        try {
            // Get registration options from server
            const response = await fetch('/api/v1/auth/webauthn/register/begin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: document.getElementById('email')?.value || 'user@example.com',
                    displayName: document.getElementById('display-name')?.value || 'User'
                })
            });

            if (!response.ok) {
                throw new Error('Failed to initiate registration');
            }

            const options = await response.json();
            
            // Convert challenge and user ID from base64url
            options.challenge = this.base64urlDecode(options.challenge);
            options.user.id = this.base64urlDecode(options.user.id);

            // Create credential
            const credential = await navigator.credentials.create({
                publicKey: options
            });

            if (!credential) {
                throw new Error('Failed to create credential');
            }

            // Send credential to server
            const registrationResponse = await fetch('/api/v1/auth/webauthn/register/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: credential.id,
                    rawId: this.arrayBufferToBase64url(credential.rawId),
                    response: {
                        clientDataJSON: this.arrayBufferToBase64url(credential.response.clientDataJSON),
                        attestationObject: this.arrayBufferToBase64url(credential.response.attestationObject)
                    },
                    type: credential.type
                })
            });

            if (!registrationResponse.ok) {
                throw new Error('Failed to complete registration');
            }

            this.showSuccess('Biometric authentication registered successfully!');
            this.showBiometricOption();

        } catch (error) {
            console.error('WebAuthn registration failed:', error);
            this.showError('Registration failed: ' + error.message);
        }
    }

    async authenticate() {
        if (!this.isSupported) {
            this.showError('WebAuthn is not supported on this device');
            return;
        }

        try {
            // Get authentication options from server
            const response = await fetch('/api/v1/auth/webauthn/authenticate/begin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to initiate authentication');
            }

            const options = await response.json();
            
            // Convert challenge from base64url
            options.challenge = this.base64urlDecode(options.challenge);
            
            // Convert credential IDs
            if (options.allowCredentials) {
                options.allowCredentials = options.allowCredentials.map(cred => ({
                    ...cred,
                    id: this.base64urlDecode(cred.id)
                }));
            }

            // Get credential
            const credential = await navigator.credentials.get({
                publicKey: options
            });

            if (!credential) {
                throw new Error('Failed to get credential');
            }

            // Send assertion to server
            const authResponse = await fetch('/api/v1/auth/webauthn/authenticate/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: credential.id,
                    rawId: this.arrayBufferToBase64url(credential.rawId),
                    response: {
                        clientDataJSON: this.arrayBufferToBase64url(credential.response.clientDataJSON),
                        authenticatorData: this.arrayBufferToBase64url(credential.response.authenticatorData),
                        signature: this.arrayBufferToBase64url(credential.response.signature),
                        userHandle: credential.response.userHandle ? 
                                   this.arrayBufferToBase64url(credential.response.userHandle) : null
                    },
                    type: credential.type
                })
            });

            if (!authResponse.ok) {
                throw new Error('Authentication failed');
            }

            const result = await authResponse.json();
            
            this.showSuccess('Authentication successful!');
            this.handleAuthSuccess(result);

        } catch (error) {
            console.error('WebAuthn authentication failed:', error);
            this.showError('Authentication failed: ' + error.message);
        }
    }

    async handleTraditionalLogin() {
        const email = document.getElementById('email')?.value;
        const password = document.getElementById('password')?.value;

        if (!email || !password) {
            this.showError('Please enter email and password');
            return;
        }

        try {
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username: email, password })
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const result = await response.json();
            this.handleAuthSuccess(result);

        } catch (error) {
            console.error('Traditional login failed:', error);
            this.showError('Login failed: ' + error.message);
        }
    }

    handleAuthSuccess(result) {
        // Store auth token
        if (result.access_token) {
            localStorage.setItem('auth_token', result.access_token);
        }

        // Update UI
        this.updateUserInterface(result.user || { name: 'User' });

        // Redirect or close modal
        const redirectUrl = new URLSearchParams(window.location.search).get('next') || '/workstation';
        window.location.href = redirectUrl;
    }

    updateUserInterface(user) {
        // Update user display
        const userDisplayName = document.getElementById('user-display-name');
        const userName = document.getElementById('user-name');
        const userEmail = document.getElementById('user-email');

        if (userDisplayName) userDisplayName.textContent = user.name || user.display_name || 'User';
        if (userName) userName.textContent = user.name || user.display_name || 'User';
        if (userEmail) userEmail.textContent = user.email || '';

        // Show authenticated state
        const guestSection = document.getElementById('guest-section');
        const authenticatedSection = document.getElementById('authenticated-section');
        const authenticatedMenu = document.getElementById('authenticated-menu');

        if (guestSection) guestSection.classList.add('hidden');
        if (authenticatedSection) authenticatedSection.classList.remove('hidden');
        if (authenticatedMenu) authenticatedMenu.classList.remove('hidden');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'error' ? 'bg-red-500 text-white' :
            type === 'success' ? 'bg-green-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Utility functions
    base64urlDecode(str) {
        const padding = '='.repeat((4 - str.length % 4) % 4);
        const base64 = (str + padding).replace(/-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray.buffer;
    }

    arrayBufferToBase64url(buffer) {
        const bytes = new Uint8Array(buffer);
        let str = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            str += String.fromCharCode(bytes[i]);
        }
        return window.btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
    }
}

// Initialize WebAuthn when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.webauthnAuth = new WebAuthnAuth();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebAuthnAuth;
}
