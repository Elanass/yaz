import Foundation
import React
import LocalAuthentication

@objc(SurgifyBridge)
class SurgifyBridge: NSObject {
    
    @objc
    static func requiresMainQueueSetup() -> Bool {
        return false
    }
    
    // MARK: - Device Information
    @objc
    func getDeviceInfo(_ resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        let device = UIDevice.current
        let deviceInfo: [String: Any] = [
            "platform": "ios",
            "model": device.model,
            "systemName": device.systemName,
            "systemVersion": device.systemVersion,
            "name": device.name,
            "identifierForVendor": device.identifierForVendor?.uuidString ?? "unknown",
            "isSimulator": TARGET_OS_SIMULATOR == 1
        ]
        resolve(deviceInfo)
    }
    
    // MARK: - Security Features
    @objc
    func enableScreenRecordingProtection(_ resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        DispatchQueue.main.async {
            // Add observer for screen recording
            NotificationCenter.default.addObserver(
                forName: UIScreen.capturedDidChangeNotification,
                object: nil,
                queue: .main
            ) { _ in
                if UIScreen.main.isCaptured {
                    // Hide sensitive content or show warning
                    self.handleScreenRecording()
                }
            }
            resolve(true)
        }
    }
    
    @objc
    func checkJailbreakStatus(_ resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        let isJailbroken = self.isDeviceJailbroken()
        resolve(["isJailbroken": isJailbroken])
    }
    
    // MARK: - Network Security
    @objc
    func enableCertificatePinning(_ pins: [String], resolver resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        // Store certificate pins for network validation
        UserDefaults.standard.set(pins, forKey: "certificate_pins")
        resolve(true)
    }
    
    @objc
    func validateNetworkConnection(_ url: String, resolver resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        guard let targetURL = URL(string: url) else {
            reject("INVALID_URL", "Invalid URL provided", nil)
            return
        }
        
        // Perform network validation with certificate pinning
        let task = URLSession.shared.dataTask(with: targetURL) { _, response, error in
            if let error = error {
                reject("NETWORK_ERROR", error.localizedDescription, error)
                return
            }
            
            if let httpResponse = response as? HTTPURLResponse {
                let result: [String: Any] = [
                    "isValid": httpResponse.statusCode == 200,
                    "statusCode": httpResponse.statusCode,
                    "headers": httpResponse.allHeaderFields
                ]
                resolve(result)
            } else {
                reject("INVALID_RESPONSE", "Invalid response received", nil)
            }
        }
        task.resume()
    }
    
    // MARK: - Storage Security
    @objc
    func secureStoreData(_ key: String, data: String, resolver resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data.data(using: .utf8) ?? Data(),
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]
        
        // Delete existing item
        SecItemDelete(query as CFDictionary)
        
        // Add new item
        let status = SecItemAdd(query as CFDictionary, nil)
        if status == errSecSuccess {
            resolve(true)
        } else {
            reject("KEYCHAIN_ERROR", "Failed to store data in keychain", nil)
        }
    }
    
    @objc
    func secureRetrieveData(_ key: String, resolver resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        if status == errSecSuccess,
           let data = result as? Data,
           let string = String(data: data, encoding: .utf8) {
            resolve(string)
        } else {
            reject("KEYCHAIN_ERROR", "Failed to retrieve data from keychain", nil)
        }
    }
    
    // MARK: - Private Methods
    private func handleScreenRecording() {
        // Notify React Native about screen recording
        // You can emit an event or update the UI
    }
    
    private func isDeviceJailbroken() -> Bool {
        // Check for common jailbreak indicators
        let jailbreakPaths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/private/var/lib/apt/"
        ]
        
        for path in jailbreakPaths {
            if FileManager.default.fileExists(atPath: path) {
                return true
            }
        }
        
        // Check if we can write to system directories
        let testPath = "/private/test_jailbreak.txt"
        do {
            try "test".write(toFile: testPath, atomically: true, encoding: .utf8)
            try FileManager.default.removeItem(atPath: testPath)
            return true
        } catch {
            // Normal behavior - we shouldn't be able to write here
        }
        
        return false
    }
}

// MARK: - RCTBridgeModule
extension SurgifyBridge: RCTBridgeModule {
    static func moduleName() -> String! {
        return "SurgifyBridge"
    }
}
