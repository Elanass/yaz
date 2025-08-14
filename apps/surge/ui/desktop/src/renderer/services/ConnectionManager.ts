import { ConnectionStatus } from '../types/global';

export class ConnectionManager {
    private listeners: Array<(status: ConnectionStatus['status']) => void> = [];
    private currentStatus: ConnectionStatus = {
        status: 'disconnected'
    };
    private reconnectInterval: number | null = null;
    private healthCheckInterval: number | null = null;

    async initialize(): Promise<void> {
        // Start connection monitoring
        this.startHealthCheck();
        
        // Listen for network changes
        window.electronAPI?.onNetworkChange((isOnline: boolean) => {
            if (isOnline) {
                this.reconnect();
            } else {
                this.setStatus('disconnected');
            }
        });

        // Initial connection attempt
        await this.connect();
    }

    async connect(): Promise<void> {
        this.setStatus('connecting');
        
        try {
            const isOnline = await window.electronAPI?.isOnline() ?? navigator.onLine;
            
            if (!isOnline) {
                this.setStatus('disconnected');
                return;
            }

            // Test connection to Surgify API
            const startTime = Date.now();
            const response = await fetch('https://api.surgify.com/health', {
                method: 'GET',
                timeout: 5000
            } as any);

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

    async reconnect(): Promise<void> {
        // Clear any existing reconnection attempts
        if (this.reconnectInterval) {
            clearInterval(this.reconnectInterval);
            this.reconnectInterval = null;
        }

        await this.connect();

        // If still not connected, schedule retry
        if (this.currentStatus.status !== 'connected') {
            this.scheduleReconnect();
        }
    }

    private scheduleReconnect(): void {
        if (this.reconnectInterval) return;

        this.reconnectInterval = setInterval(async () => {
            await this.connect();
            
            if (this.currentStatus.status === 'connected') {
                if (this.reconnectInterval) {
                    clearInterval(this.reconnectInterval);
                    this.reconnectInterval = null;
                }
            }
        }, 10000); // Retry every 10 seconds
    }

    private startHealthCheck(): void {
        this.healthCheckInterval = setInterval(async () => {
            if (this.currentStatus.status === 'connected') {
                try {
                    const startTime = Date.now();
                    const response = await fetch('https://api.surgify.com/health', {
                        method: 'GET',
                        timeout: 3000
                    } as any);

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
        }, 30000); // Health check every 30 seconds
    }

    getStatus(): ConnectionStatus {
        return this.currentStatus;
    }

    onStatusChange(callback: (status: ConnectionStatus['status']) => void): void {
        this.listeners.push(callback);
    }

    private setStatus(status: ConnectionStatus['status']): void {
        this.currentStatus.status = status;
        this.notifyListeners(status);
    }

    private notifyListeners(status: ConnectionStatus['status']): void {
        this.listeners.forEach(callback => callback(status));
    }

    destroy(): void {
        if (this.reconnectInterval) {
            clearInterval(this.reconnectInterval);
        }
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
    }
}
