/**
 * Device Security Service
 * Provides security features and device information
 */

import { Platform } from 'react-native';
import { SurgifyBridge, DeviceInfo, SecurityStatus, NetworkValidationResult, SecurityError } from './NativeModules';

export class DeviceSecurityService {
  private static certificatePins: string[] = [];

  // Device Information
  static async getDeviceInfo(): Promise<DeviceInfo | null> {
    try {
      return await SurgifyBridge.getDeviceInfo();
    } catch (error) {
      console.warn('DeviceSecurityService.getDeviceInfo error:', error);
      return null;
    }
  }

  // Security Status Checks
  static async checkDeviceCompromise(): Promise<SecurityStatus> {
    try {
      if (Platform.OS === 'ios') {
        return await SurgifyBridge.checkJailbreakStatus?.() || { isJailbroken: false };
      } else {
        return await SurgifyBridge.checkRootStatus?.() || { isRooted: false };
      }
    } catch (error) {
      console.warn('DeviceSecurityService.checkDeviceCompromise error:', error);
      return Platform.OS === 'ios' ? { isJailbroken: false } : { isRooted: false };
    }
  }

  static async isDeviceSecure(): Promise<boolean> {
    const status = await this.checkDeviceCompromise();
    if (Platform.OS === 'ios') {
      return !status.isJailbroken;
    } else {
      return !status.isRooted;
    }
  }

  // Screen Protection
  static async enableScreenProtection(): Promise<boolean> {
    try {
      return await SurgifyBridge.enableScreenRecordingProtection();
    } catch (error) {
      console.warn('DeviceSecurityService.enableScreenProtection error:', error);
      return false;
    }
  }

  // Network Security
  static async setCertificatePins(pins: string[]): Promise<boolean> {
    try {
      this.certificatePins = pins;
      return await SurgifyBridge.enableCertificatePinning(pins);
    } catch (error) {
      console.warn('DeviceSecurityService.setCertificatePins error:', error);
      return false;
    }
  }

  static async validateServerConnection(url: string): Promise<NetworkValidationResult | null> {
    try {
      return await SurgifyBridge.validateNetworkConnection(url);
    } catch (error) {
      console.warn('DeviceSecurityService.validateServerConnection error:', error);
      return null;
    }
  }

  // Secure Storage
  static async securelyStore(key: string, data: string): Promise<boolean> {
    try {
      return await SurgifyBridge.secureStoreData(key, data);
    } catch (error) {
      console.warn('DeviceSecurityService.securelyStore error:', error);
      return false;
    }
  }

  static async securelyRetrieve(key: string): Promise<string | null> {
    try {
      return await SurgifyBridge.secureRetrieveData(key);
    } catch (error) {
      if (error.code === SecurityError.DATA_NOT_FOUND) {
        return null; // Data not found is expected
      }
      console.warn('DeviceSecurityService.securelyRetrieve error:', error);
      return null;
    }
  }

  // Security Validation Methods
  static async performSecurityChecks(): Promise<{
    isSecure: boolean;
    issues: string[];
    recommendations: string[];
  }> {
    const issues: string[] = [];
    const recommendations: string[] = [];

    // Check device compromise
    const compromiseStatus = await this.checkDeviceCompromise();
    if (Platform.OS === 'ios' && compromiseStatus.isJailbroken) {
      issues.push('Device appears to be jailbroken');
      recommendations.push('Use a non-jailbroken device for security');
    } else if (Platform.OS === 'android' && compromiseStatus.isRooted) {
      issues.push('Device appears to be rooted');
      recommendations.push('Use a non-rooted device for security');
    }

    // Check if screen protection is enabled
    const screenProtected = await this.enableScreenProtection();
    if (!screenProtected) {
      issues.push('Screen recording protection could not be enabled');
      recommendations.push('Ensure app has proper security permissions');
    }

    // Get device info for additional checks
    const deviceInfo = await this.getDeviceInfo();
    if (deviceInfo?.isSimulator || deviceInfo?.isEmulator) {
      issues.push('Running on simulator/emulator');
      recommendations.push('Use a physical device for production');
    }

    return {
      isSecure: issues.length === 0,
      issues,
      recommendations
    };
  }

  // Certificate Pinning Helpers
  static async validateApiEndpoint(baseUrl: string): Promise<boolean> {
    if (this.certificatePins.length === 0) {
      console.warn('No certificate pins configured');
      return false;
    }

    const result = await this.validateServerConnection(baseUrl);
    return result?.isValid === true;
  }
}

export default DeviceSecurityService;
