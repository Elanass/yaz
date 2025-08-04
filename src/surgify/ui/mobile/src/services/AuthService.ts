/**
 * Authentication Service - Handle user authentication and session management
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import {Alert} from 'react-native';
import axios from 'axios';

interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthResponse {
  success: boolean;
  token?: string;
  user?: {
    id: string;
    username: string;
    email: string;
    role: string;
  };
  message?: string;
}

class AuthService {
  private static readonly API_BASE = 'https://surgify.local/api/v1';
  private static readonly TOKEN_KEY = 'surgify_auth_token';
  private static readonly USER_KEY = 'surgify_user_data';
  private static readonly CREDENTIALS_KEY = 'surgify_credentials';

  /**
   * Login with username and password
   */
  static async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await axios.post(`${this.API_BASE}/auth/login`, {
        username: credentials.username,
        password: credentials.password,
        device_type: 'mobile',
        platform: 'react-native',
      });

      if (response.data.success) {
        // Store authentication data
        await AsyncStorage.setItem(this.TOKEN_KEY, response.data.token);
        await AsyncStorage.setItem(this.USER_KEY, JSON.stringify(response.data.user));
        
        // Store encrypted credentials for biometric login
        await this.storeCredentials(credentials);

        return response.data;
      } else {
        throw new Error(response.data.message || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw new Error('Login failed. Please check your credentials and try again.');
    }
  }

  /**
   * Logout user and clear stored data
   */
  static async logout(): Promise<void> {
    try {
      const token = await AsyncStorage.getItem(this.TOKEN_KEY);
      
      // Notify server about logout
      if (token) {
        try {
          await axios.post(`${this.API_BASE}/auth/logout`, {}, {
            headers: {Authorization: `Bearer ${token}`},
          });
        } catch (error) {
          console.log('Server logout failed, continuing with local logout');
        }
      }

      // Clear all stored data
      await AsyncStorage.multiRemove([
        this.TOKEN_KEY,
        this.USER_KEY,
        this.CREDENTIALS_KEY,
      ]);
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  /**
   * Check if user is authenticated
   */
  static async isAuthenticated(): Promise<boolean> {
    try {
      const token = await AsyncStorage.getItem(this.TOKEN_KEY);
      
      if (!token) {
        return false;
      }

      // Verify token with server
      const response = await axios.get(`${this.API_BASE}/auth/verify`, {
        headers: {Authorization: `Bearer ${token}`},
      });

      return response.data.valid === true;
    } catch (error) {
      console.error('Auth verification error:', error);
      // If token verification fails, clear stored data
      await this.logout();
      return false;
    }
  }

  /**
   * Get current user data
   */
  static async getCurrentUser(): Promise<any> {
    try {
      const userData = await AsyncStorage.getItem(this.USER_KEY);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Get user error:', error);
      return null;
    }
  }

  /**
   * Get current auth token
   */
  static async getToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(this.TOKEN_KEY);
    } catch (error) {
      console.error('Get token error:', error);
      return null;
    }
  }

  /**
   * Refresh authentication token
   */
  static async refreshToken(): Promise<boolean> {
    try {
      const token = await AsyncStorage.getItem(this.TOKEN_KEY);
      
      if (!token) {
        return false;
      }

      const response = await axios.post(`${this.API_BASE}/auth/refresh`, {}, {
        headers: {Authorization: `Bearer ${token}`},
      });

      if (response.data.success) {
        await AsyncStorage.setItem(this.TOKEN_KEY, response.data.token);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  }

  /**
   * Store credentials for biometric authentication
   */
  private static async storeCredentials(credentials: LoginCredentials): Promise<void> {
    try {
      // In a real implementation, you would encrypt these credentials
      // For demo purposes, we're storing them as-is
      // Use a proper encryption library like react-native-keychain
      await AsyncStorage.setItem(this.CREDENTIALS_KEY, JSON.stringify(credentials));
    } catch (error) {
      console.error('Store credentials error:', error);
    }
  }

  /**
   * Get stored credentials for biometric authentication
   */
  static async getStoredCredentials(): Promise<LoginCredentials | null> {
    try {
      const credentials = await AsyncStorage.getItem(this.CREDENTIALS_KEY);
      return credentials ? JSON.parse(credentials) : null;
    } catch (error) {
      console.error('Get credentials error:', error);
      return null;
    }
  }

  /**
   * Clear stored credentials
   */
  static async clearStoredCredentials(): Promise<void> {
    try {
      await AsyncStorage.removeItem(this.CREDENTIALS_KEY);
    } catch (error) {
      console.error('Clear credentials error:', error);
    }
  }

  /**
   * Setup axios interceptors for automatic token handling
   */
  static setupInterceptors(): void {
    // Request interceptor to add auth header
    axios.interceptors.request.use(
      async (config) => {
        const token = await this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token expiration
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          const refreshed = await this.refreshToken();
          if (refreshed) {
            const token = await this.getToken();
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return axios(originalRequest);
          } else {
            // Refresh failed, logout user
            await this.logout();
            Alert.alert('Session Expired', 'Please log in again.');
          }
        }

        return Promise.reject(error);
      }
    );
  }
}

export default AuthService;
