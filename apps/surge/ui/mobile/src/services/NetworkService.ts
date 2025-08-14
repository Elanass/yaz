/**
 * Network Service - Handle network connectivity and API requests
 */

import NetInfo from '@react-native-netinfo/netinfo';
import {Alert} from 'react-native';

interface NetworkState {
  isConnected: boolean;
  isInternetReachable: boolean;
  type: string;
  details: any;
}

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  status?: number;
}

class NetworkService {
  private static networkListeners: Array<(state: NetworkState) => void> = [];
  private static currentNetworkState: NetworkState | null = null;

  /**
   * Initialize network monitoring
   */
  static initialize(): void {
    NetInfo.addEventListener(state => {
      const networkState: NetworkState = {
        isConnected: state.isConnected || false,
        isInternetReachable: state.isInternetReachable || false,
        type: state.type,
        details: state.details,
      };

      this.currentNetworkState = networkState;
      this.notifyListeners(networkState);
    });
  }

  /**
   * Check current connectivity status
   */
  static async checkConnectivity(): Promise<boolean> {
    try {
      const state = await NetInfo.fetch();
      return state.isConnected && state.isInternetReachable;
    } catch (error) {
      console.error('Connectivity check error:', error);
      return false;
    }
  }

  /**
   * Get current network state
   */
  static async getNetworkState(): Promise<NetworkState> {
    try {
      const state = await NetInfo.fetch();
      return {
        isConnected: state.isConnected || false,
        isInternetReachable: state.isInternetReachable || false,
        type: state.type,
        details: state.details,
      };
    } catch (error) {
      console.error('Get network state error:', error);
      return {
        isConnected: false,
        isInternetReachable: false,
        type: 'none',
        details: null,
      };
    }
  }

  /**
   * Add network state listener
   */
  static addNetworkListener(listener: (state: NetworkState) => void): void {
    this.networkListeners.push(listener);
  }

  /**
   * Remove network state listener
   */
  static removeNetworkListener(listener: (state: NetworkState) => void): void {
    const index = this.networkListeners.indexOf(listener);
    if (index > -1) {
      this.networkListeners.splice(index, 1);
    }
  }

  /**
   * Notify all listeners of network state changes
   */
  private static notifyListeners(state: NetworkState): void {
    this.networkListeners.forEach(listener => {
      try {
        listener(state);
      } catch (error) {
        console.error('Network listener error:', error);
      }
    });
  }

  /**
   * Check if device has internet connection
   */
  static async hasInternetConnection(): Promise<boolean> {
    try {
      const state = await NetInfo.fetch();
      return state.isConnected && state.isInternetReachable;
    } catch (error) {
      console.error('Internet connection check error:', error);
      return false;
    }
  }

  /**
   * Get connection type (wifi, cellular, etc.)
   */
  static async getConnectionType(): Promise<string> {
    try {
      const state = await NetInfo.fetch();
      return state.type;
    } catch (error) {
      console.error('Get connection type error:', error);
      return 'unknown';
    }
  }

  /**
   * Check if device is on WiFi
   */
  static async isOnWiFi(): Promise<boolean> {
    try {
      const state = await NetInfo.fetch();
      return state.type === 'wifi' && state.isConnected;
    } catch (error) {
      console.error('WiFi check error:', error);
      return false;
    }
  }

  /**
   * Check if device is on cellular
   */
  static async isOnCellular(): Promise<boolean> {
    try {
      const state = await NetInfo.fetch();
      return state.type === 'cellular' && state.isConnected;
    } catch (error) {
      console.error('Cellular check error:', error);
      return false;
    }
  }

  /**
   * Show network error alert
   */
  static showNetworkError(): void {
    Alert.alert(
      'No Internet Connection',
      'Please check your internet connection and try again.',
      [
        {text: 'OK', style: 'default'},
        {
          text: 'Retry',
          onPress: async () => {
            const isConnected = await this.checkConnectivity();
            if (!isConnected) {
              this.showNetworkError();
            }
          },
        },
      ]
    );
  }

  /**
   * Execute request with network check
   */
  static async executeWithNetworkCheck<T>(
    request: () => Promise<T>
  ): Promise<ApiResponse<T>> {
    try {
      const isConnected = await this.checkConnectivity();
      
      if (!isConnected) {
        return {
          success: false,
          error: 'No internet connection available',
          status: 0,
        };
      }

      const result = await request();
      return {
        success: true,
        data: result,
      };
    } catch (error) {
      console.error('Network request error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network request failed',
        status: error.response?.status || 0,
      };
    }
  }

  /**
   * Download speed test (simple)
   */
  static async testDownloadSpeed(): Promise<number> {
    try {
      const startTime = Date.now();
      const testUrl = 'https://surgify.local/api/v1/health/speed-test';
      
      const response = await fetch(testUrl, {
        method: 'GET',
        cache: 'no-cache',
      });
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      const bytes = parseInt(response.headers.get('content-length') || '0', 10);
      
      // Calculate speed in Mbps
      const bitsPerSecond = (bytes * 8) / (duration / 1000);
      const mbps = bitsPerSecond / (1024 * 1024);
      
      return mbps;
    } catch (error) {
      console.error('Speed test error:', error);
      return 0;
    }
  }

  /**
   * Get network quality indicator
   */
  static async getNetworkQuality(): Promise<'excellent' | 'good' | 'fair' | 'poor' | 'offline'> {
    try {
      const isConnected = await this.checkConnectivity();
      
      if (!isConnected) {
        return 'offline';
      }

      const speed = await this.testDownloadSpeed();
      
      if (speed > 10) {
        return 'excellent';
      } else if (speed > 5) {
        return 'good';
      } else if (speed > 1) {
        return 'fair';
      } else {
        return 'poor';
      }
    } catch (error) {
      console.error('Network quality check error:', error);
      return 'poor';
    }
  }

  /**
   * Monitor network changes and show appropriate messages
   */
  static startNetworkMonitoring(): void {
    this.addNetworkListener((state) => {
      if (!state.isConnected) {
        Alert.alert(
          'Connection Lost',
          'You are now offline. Some features may not be available.',
          [{text: 'OK', style: 'default'}]
        );
      } else if (this.currentNetworkState && !this.currentNetworkState.isConnected) {
        Alert.alert(
          'Connection Restored',
          'You are now back online.',
          [{text: 'OK', style: 'default'}]
        );
      }
    });
  }

  /**
   * Stop network monitoring
   */
  static stopNetworkMonitoring(): void {
    this.networkListeners = [];
  }
}

export default NetworkService;
