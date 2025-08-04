import Foundation
import React
import LocalAuthentication

@objc(BiometricModule)
class BiometricModule: NSObject {
    
    @objc
    static func requiresMainQueueSetup() -> Bool {
        return false
    }
    
    @objc
    func isAvailable(_ resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        let context = LAContext()
        var error: NSError?
        
        let isAvailable = context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
        
        var biometryType = "none"
        if isAvailable {
            switch context.biometryType {
            case .faceID:
                biometryType = "faceID"
            case .touchID:
                biometryType = "touchID"
            default:
                biometryType = "unknown"
            }
        }
        
        let result: [String: Any] = [
            "isAvailable": isAvailable,
            "biometryType": biometryType,
            "error": error?.localizedDescription ?? NSNull()
        ]
        
        resolve(result)
    }
    
    @objc
    func authenticate(_ reason: String, resolver resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        let context = LAContext()
        
        // Configure authentication context
        context.localizedFallbackTitle = "Use Passcode"
        context.localizedCancelTitle = "Cancel"
        
        context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { success, error in
            DispatchQueue.main.async {
                if success {
                    resolve([
                        "success": true,
                        "method": self.getBiometryTypeString(context.biometryType)
                    ])
                } else {
                    let errorCode = self.getErrorCode(error)
                    let errorMessage = error?.localizedDescription ?? "Authentication failed"
                    
                    reject(errorCode, errorMessage, error)
                }
            }
        }
    }
    
    @objc
    func authenticateWithPasscode(_ reason: String, resolver resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        let context = LAContext()
        
        context.evaluatePolicy(.deviceOwnerAuthentication, localizedReason: reason) { success, error in
            DispatchQueue.main.async {
                if success {
                    resolve([
                        "success": true,
                        "method": "passcode"
                    ])
                } else {
                    let errorCode = self.getErrorCode(error)
                    let errorMessage = error?.localizedDescription ?? "Authentication failed"
                    
                    reject(errorCode, errorMessage, error)
                }
            }
        }
    }
    
    // MARK: - Private Methods
    private func getBiometryTypeString(_ biometryType: LABiometryType) -> String {
        switch biometryType {
        case .faceID:
            return "faceID"
        case .touchID:
            return "touchID"
        default:
            return "unknown"
        }
    }
    
    private func getErrorCode(_ error: Error?) -> String {
        guard let laError = error as? LAError else {
            return "UNKNOWN_ERROR"
        }
        
        switch laError.code {
        case .authenticationFailed:
            return "AUTHENTICATION_FAILED"
        case .userCancel:
            return "USER_CANCELLED"
        case .userFallback:
            return "USER_FALLBACK"
        case .systemCancel:
            return "SYSTEM_CANCELLED"
        case .passcodeNotSet:
            return "PASSCODE_NOT_SET"
        case .biometryNotAvailable:
            return "BIOMETRY_NOT_AVAILABLE"
        case .biometryNotEnrolled:
            return "BIOMETRY_NOT_ENROLLED"
        case .biometryLockout:
            return "BIOMETRY_LOCKOUT"
        case .appCancel:
            return "APP_CANCELLED"
        case .invalidContext:
            return "INVALID_CONTEXT"
        case .notInteractive:
            return "NOT_INTERACTIVE"
        default:
            return "UNKNOWN_ERROR"
        }
    }
}

// MARK: - RCTBridgeModule
extension BiometricModule: RCTBridgeModule {
    static func moduleName() -> String! {
        return "BiometricModule"
    }
}
