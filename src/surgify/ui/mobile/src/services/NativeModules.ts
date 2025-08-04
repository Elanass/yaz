import { NativeModules } from 'react-native';

// Device Information Interface
export interface DeviceInfo {
  platform: 'ios' | 'android';
  model: string;
  systemName: string;
  systemVersion: string;
  name?: string;
  manufacturer?: string;
  brand?: string;
  apiLevel?: number;
  identifierForVendor?: string;
  androidId?: string;
  isSimulator?: boolean;
  isEmulator?: boolean;
}

// Security Interfaces
export interface SecurityStatus {
  isJailbroken?: boolean;
  isRooted?: boolean;
}

export interface NetworkValidationResult {
  isValid: boolean;
  statusCode: number;
  headers: Record<string, string>;
}

// Biometric Interfaces
export interface BiometricAvailability {
  isAvailable: boolean;
  biometryType: 'faceID' | 'touchID' | 'fingerprint' | 'face' | 'both' | 'none' | 'unknown';
  hasFingerprint?: boolean;
  hasFace?: boolean;
  hasPermission?: boolean;
  error?: string;
}

export interface BiometricAuthResult {
  success: boolean;
  method: 'faceID' | 'touchID' | 'fingerprint' | 'face' | 'biometric' | 'passcode';
}

// Camera Interfaces
export interface CameraPermissions {
  camera: 'granted' | 'denied' | 'undetermined' | 'restricted';
  storage?: 'granted' | 'denied' | 'undetermined' | 'restricted';
}

export interface CameraOptions {
  quality?: 'high' | 'medium' | 'low';
  cameraType?: 'front' | 'back';
  allowsEditing?: boolean;
}

export interface CameraResult {
  uri: string;
  width: number;
  height: number;
  type: string;
}

// Native Module Interfaces
interface ISurgifyBridge {
  getDeviceInfo(): Promise<DeviceInfo>;
  enableScreenRecordingProtection(): Promise<boolean>;
  checkJailbreakStatus?(): Promise<SecurityStatus>;
  checkRootStatus?(): Promise<SecurityStatus>;
  enableCertificatePinning(pins: string[]): Promise<boolean>;
  validateNetworkConnection(url: string): Promise<NetworkValidationResult>;
  secureStoreData(key: string, data: string): Promise<boolean>;
  secureRetrieveData(key: string): Promise<string>;
}

interface IBiometricModule {
  isAvailable(): Promise<BiometricAvailability>;
  authenticate(reason: string): Promise<BiometricAuthResult>;
  authenticateWithPasscode(reason: string): Promise<BiometricAuthResult>;
}

interface ICameraModule {
  checkPermissions(): Promise<CameraPermissions>;
  requestPermissions(): Promise<CameraPermissions>;
  openCamera(options: CameraOptions): Promise<CameraResult>;
  openGallery?(options: CameraOptions): Promise<CameraResult>;
  captureImage(options: CameraOptions): Promise<CameraResult>;
}

// Export native modules with proper typing
export const SurgifyBridge: ISurgifyBridge = NativeModules.SurgifyBridge;
export const BiometricModule: IBiometricModule = NativeModules.BiometricModule;
export const CameraModule: ICameraModule = NativeModules.CameraModule;

// Error types for better error handling
export enum BiometricError {
  AUTHENTICATION_FAILED = 'AUTHENTICATION_FAILED',
  USER_CANCELLED = 'USER_CANCELLED',
  USER_FALLBACK = 'USER_FALLBACK',
  SYSTEM_CANCELLED = 'SYSTEM_CANCELLED',
  PASSCODE_NOT_SET = 'PASSCODE_NOT_SET',
  BIOMETRY_NOT_AVAILABLE = 'BIOMETRY_NOT_AVAILABLE',
  BIOMETRY_NOT_ENROLLED = 'BIOMETRY_NOT_ENROLLED',
  BIOMETRY_LOCKOUT = 'BIOMETRY_LOCKOUT',
  BIOMETRY_LOCKOUT_PERMANENT = 'BIOMETRY_LOCKOUT_PERMANENT',
  APP_CANCELLED = 'APP_CANCELLED',
  INVALID_CONTEXT = 'INVALID_CONTEXT',
  NOT_INTERACTIVE = 'NOT_INTERACTIVE',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

export enum CameraError {
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  CAMERA_NOT_AVAILABLE = 'CAMERA_NOT_AVAILABLE',
  USER_CANCELLED = 'USER_CANCELLED',
  NO_ACTIVITY = 'NO_ACTIVITY',
  NO_VIEW_CONTROLLER = 'NO_VIEW_CONTROLLER',
  IMAGE_PROCESSING_ERROR = 'IMAGE_PROCESSING_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

export enum SecurityError {
  DEVICE_COMPROMISED = 'DEVICE_COMPROMISED',
  NETWORK_ERROR = 'NETWORK_ERROR',
  CERT_PIN_MISMATCH = 'CERT_PIN_MISMATCH',
  SECURE_STORAGE_ERROR = 'SECURE_STORAGE_ERROR',
  DATA_NOT_FOUND = 'DATA_NOT_FOUND'
}
