/**
 * Camera Service
 * Provides camera functionality with permission handling
 */

import { Platform } from 'react-native';
import { CameraModule, CameraPermissions, CameraOptions, CameraResult, CameraError } from './NativeModules';

export interface CameraServiceResult {
  success: boolean;
  data?: CameraResult;
  error?: string;
}

export class CameraService {
  // Permission Management
  static async checkPermissions(): Promise<CameraPermissions> {
    try {
      return await CameraModule.checkPermissions();
    } catch (error) {
      console.warn('CameraService.checkPermissions error:', error);
      return { camera: 'denied' };
    }
  }

  static async requestPermissions(): Promise<CameraPermissions> {
    try {
      return await CameraModule.requestPermissions();
    } catch (error) {
      console.warn('CameraService.requestPermissions error:', error);
      return { camera: 'denied' };
    }
  }

  static async hasPermission(): Promise<boolean> {
    const permissions = await this.checkPermissions();
    return permissions.camera === 'granted';
  }

  // Camera Operations
  static async openCamera(options: CameraOptions = {}): Promise<CameraServiceResult> {
    try {
      // Check permissions first
      const hasPermission = await this.hasPermission();
      if (!hasPermission) {
        const permissions = await this.requestPermissions();
        if (permissions.camera !== 'granted') {
          return {
            success: false,
            error: 'Camera permission denied'
          };
        }
      }

      const result = await CameraModule.openCamera(options);
      return {
        success: true,
        data: result
      };
    } catch (error: any) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      };
    }
  }

  static async captureImage(options: CameraOptions = {}): Promise<CameraServiceResult> {
    try {
      // Check permissions first
      const hasPermission = await this.hasPermission();
      if (!hasPermission) {
        const permissions = await this.requestPermissions();
        if (permissions.camera !== 'granted') {
          return {
            success: false,
            error: 'Camera permission denied'
          };
        }
      }

      const result = await CameraModule.captureImage(options);
      return {
        success: true,
        data: result
      };
    } catch (error: any) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      };
    }
  }

  static async openGallery(options: CameraOptions = {}): Promise<CameraServiceResult> {
    try {
      // For Android, check storage permission if needed
      if (Platform.OS === 'android') {
        const permissions = await this.checkPermissions();
        if (permissions.storage && permissions.storage !== 'granted') {
          const newPermissions = await this.requestPermissions();
          if (newPermissions.storage !== 'granted') {
            return {
              success: false,
              error: 'Storage permission denied'
            };
          }
        }
      }

      // Check if gallery method exists (Android-specific)
      if (CameraModule.openGallery) {
        const result = await CameraModule.openGallery(options);
        return {
          success: true,
          data: result
        };
      } else {
        return {
          success: false,
          error: 'Gallery access not available on this platform'
        };
      }
    } catch (error: any) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      };
    }
  }

  // Helper Methods
  private static getErrorMessage(error: any): string {
    if (error.code) {
      switch (error.code) {
        case CameraError.PERMISSION_DENIED:
          return 'Camera permission is required to take photos';
        case CameraError.CAMERA_NOT_AVAILABLE:
          return 'Camera is not available on this device';
        case CameraError.USER_CANCELLED:
          return 'User cancelled camera operation';
        case CameraError.NO_ACTIVITY:
        case CameraError.NO_VIEW_CONTROLLER:
          return 'Unable to present camera interface';
        case CameraError.IMAGE_PROCESSING_ERROR:
          return 'Failed to process captured image';
        default:
          return error.message || 'Camera operation failed';
      }
    }
    return error.message || 'Unknown camera error';
  }

  // Utility methods
  static async getDefaultCameraOptions(): Promise<CameraOptions> {
    return {
      quality: 'medium',
      cameraType: 'back',
      allowsEditing: false
    };
  }

  static async getHighQualityOptions(): Promise<CameraOptions> {
    return {
      quality: 'high',
      cameraType: 'back',
      allowsEditing: true
    };
  }

  static async getFrontCameraOptions(): Promise<CameraOptions> {
    return {
      quality: 'medium',
      cameraType: 'front',
      allowsEditing: false
    };
  }

  // Validation
  static validateCameraResult(result: CameraResult): boolean {
    return !!(result.uri && result.width && result.height && result.type);
  }

  static getImageSizeInMB(result: CameraResult): number {
    if (!result.uri || !result.uri.startsWith('data:')) {
      return 0;
    }
    
    // Rough calculation for base64 encoded images
    const base64Data = result.uri.split(',')[1];
    if (!base64Data) return 0;
    
    const sizeInBytes = (base64Data.length * 3) / 4;
    return sizeInBytes / (1024 * 1024); // Convert to MB
  }
}

export default CameraService;
