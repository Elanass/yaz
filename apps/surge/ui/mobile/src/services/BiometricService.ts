/**
 * Biometric Authentication Service
 * Uses native modules for secure biometric authentication
 */

import { Platform } from 'react-native';
import { BiometricModule, BiometricAvailability, BiometricAuthResult, BiometricError } from './NativeModules';

interface BiometricResult {
  success: boolean;
  error?: string;
  method?: string;
}

export class BiometricService {
  static async isAvailable(): Promise<boolean> {
    try {
      const availability: BiometricAvailability = await BiometricModule.isAvailable();
      return availability.isAvailable;
    } catch (error) {
      console.warn('BiometricService.isAvailable error:', error);
      return false;
    }
  }

  static async getAvailabilityDetails(): Promise<BiometricAvailability | null> {
    try {
      return await BiometricModule.isAvailable();
    } catch (error) {
      console.warn('BiometricService.getAvailabilityDetails error:', error);
      return null;
    }
  }

  static async authenticate(reason: string): Promise<BiometricResult> {
    try {
      const result: BiometricAuthResult = await BiometricModule.authenticate(reason);
      return { 
        success: result.success,
        method: result.method
      };
    } catch (error: any) {
      let errorMessage = 'Authentication failed';
      
      // Handle specific error types
      if (error.code) {
        switch (error.code) {
          case BiometricError.USER_CANCELLED:
            errorMessage = 'Authentication was cancelled by user';
            break;
          case BiometricError.BIOMETRY_NOT_AVAILABLE:
            errorMessage = 'Biometric authentication is not available';
            break;
          case BiometricError.BIOMETRY_NOT_ENROLLED:
            errorMessage = 'No biometric credentials are enrolled';
            break;
          case BiometricError.BIOMETRY_LOCKOUT:
            errorMessage = 'Biometric authentication is temporarily locked';
            break;
          default:
            errorMessage = error.message || errorMessage;
        }
      }
      
      return { 
        success: false, 
        error: errorMessage
      };
    }
  }

  static async authenticateWithPasscode(reason: string): Promise<BiometricResult> {
    try {
      const result: BiometricAuthResult = await BiometricModule.authenticateWithPasscode(reason);
      return { 
        success: result.success,
        method: result.method
      };
    } catch (error: any) {
      return { 
        success: false, 
        error: error.message || 'Passcode authentication failed'
      };
    }
  }
}

export default BiometricService;
