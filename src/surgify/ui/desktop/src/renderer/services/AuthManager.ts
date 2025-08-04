import { AuthStatus, UserInfo } from '../types/global';

export class AuthManager {
    private listeners: Array<(isAuthenticated: boolean, userInfo: UserInfo | null) => void> = [];
    private currentAuthStatus: AuthStatus = {
        isAuthenticated: false,
        userInfo: null
    };

    async initialize(): Promise<void> {
        // Check for existing auth token
        try {
            const token = await window.electronAPI?.getAuthToken();
            if (token) {
                // Validate token with backend
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

    async checkAuthStatus(): Promise<AuthStatus> {
        return this.currentAuthStatus;
    }

    async login(credentials: { email: string; password: string }): Promise<AuthStatus> {
        try {
            // This would typically make a request to your auth endpoint
            // For now, we'll simulate the process
            const response = await fetch('https://api.surgify.com/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            if (response.ok) {
                const data = await response.json();
                const authStatus: AuthStatus = {
                    isAuthenticated: true,
                    userInfo: data.user,
                    token: data.token
                };

                // Store token securely
                await window.electronAPI?.setAuthToken(data.token);
                
                this.currentAuthStatus = authStatus;
                this.notifyListeners(true, data.user);
                
                return authStatus;
            } else {
                throw new Error('Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    async logout(): Promise<void> {
        try {
            // Clear stored token
            await window.electronAPI?.clearAuthToken();
            
            // Reset auth status
            this.currentAuthStatus = {
                isAuthenticated: false,
                userInfo: null
            };
            
            this.notifyListeners(false, null);
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    private async validateToken(token: string): Promise<UserInfo | null> {
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

    onAuthChange(callback: (isAuthenticated: boolean, userInfo: UserInfo | null) => void): void {
        this.listeners.push(callback);
    }

    private notifyListeners(isAuthenticated: boolean, userInfo: UserInfo | null): void {
        this.listeners.forEach(callback => callback(isAuthenticated, userInfo));
    }
}
