import Foundation
import React
import AVFoundation
import UIKit

@objc(CameraModule)
class CameraModule: NSObject {
    
    @objc
    static func requiresMainQueueSetup() -> Bool {
        return true
    }
    
    @objc
    func checkPermissions(_ resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        let status = AVCaptureDevice.authorizationStatus(for: .video)
        
        var permissionStatus = "unknown"
        switch status {
        case .authorized:
            permissionStatus = "granted"
        case .denied:
            permissionStatus = "denied"
        case .restricted:
            permissionStatus = "restricted"
        case .notDetermined:
            permissionStatus = "undetermined"
        @unknown default:
            permissionStatus = "unknown"
        }
        
        resolve([
            "camera": permissionStatus
        ])
    }
    
    @objc
    func requestPermissions(_ resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        AVCaptureDevice.requestAccess(for: .video) { granted in
            DispatchQueue.main.async {
                resolve([
                    "camera": granted ? "granted" : "denied"
                ])
            }
        }
    }
    
    @objc
    func openCamera(_ options: [String: Any], resolver resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        DispatchQueue.main.async {
            guard let topViewController = self.getTopViewController() else {
                reject("NO_VIEW_CONTROLLER", "No view controller available", nil)
                return
            }
            
            guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
                reject("CAMERA_NOT_AVAILABLE", "Camera is not available", nil)
                return
            }
            
            let picker = UIImagePickerController()
            picker.sourceType = .camera
            picker.mediaTypes = ["public.image"]
            
            // Configure camera options
            if let quality = options["quality"] as? String {
                switch quality {
                case "high":
                    picker.cameraCaptureMode = .photo
                case "medium":
                    picker.cameraCaptureMode = .photo
                case "low":
                    picker.cameraCaptureMode = .photo
                default:
                    picker.cameraCaptureMode = .photo
                }
            }
            
            if let cameraType = options["cameraType"] as? String {
                switch cameraType {
                case "front":
                    picker.cameraDevice = .front
                case "back":
                    picker.cameraDevice = .rear
                default:
                    picker.cameraDevice = .rear
                }
            }
            
            // Set delegate to handle image capture
            let delegate = CameraDelegate(resolve: resolve, reject: reject)
            picker.delegate = delegate
            
            // Keep a strong reference to the delegate
            objc_setAssociatedObject(picker, "delegate", delegate, .OBJC_ASSOCIATION_RETAIN_NONATOMIC)
            
            topViewController.present(picker, animated: true)
        }
    }
    
    @objc
    func captureImage(_ options: [String: Any], resolver resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) {
        // For more advanced camera functionality, you would implement a custom camera view
        // For now, we'll use the simple image picker approach
        self.openCamera(options, resolver: resolve, rejecter: reject)
    }
    
    // MARK: - Private Methods
    private func getTopViewController() -> UIViewController? {
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
              let window = windowScene.windows.first else {
            return nil
        }
        
        var topViewController = window.rootViewController
        while let presentedViewController = topViewController?.presentedViewController {
            topViewController = presentedViewController
        }
        
        return topViewController
    }
}

// MARK: - RCTBridgeModule
extension CameraModule: RCTBridgeModule {
    static func moduleName() -> String! {
        return "CameraModule"
    }
}

// MARK: - Camera Delegate
class CameraDelegate: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
    
    private let resolve: RCTPromiseResolveBlock
    private let reject: RCTPromiseRejectBlock
    
    init(resolve: @escaping RCTPromiseResolveBlock, reject: @escaping RCTPromiseRejectBlock) {
        self.resolve = resolve
        self.reject = reject
        super.init()
    }
    
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
        picker.dismiss(animated: true) {
            guard let image = info[.originalImage] as? UIImage else {
                self.reject("NO_IMAGE", "No image captured", nil)
                return
            }
            
            // Convert image to base64 or save to file
            guard let imageData = image.jpegData(compressionQuality: 0.8) else {
                self.reject("IMAGE_PROCESSING_ERROR", "Failed to process image", nil)
                return
            }
            
            let base64String = imageData.base64EncodedString()
            
            let result: [String: Any] = [
                "uri": "data:image/jpeg;base64,\(base64String)",
                "width": image.size.width,
                "height": image.size.height,
                "type": "image/jpeg"
            ]
            
            self.resolve(result)
        }
    }
    
    func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
        picker.dismiss(animated: true) {
            self.reject("USER_CANCELLED", "User cancelled camera", nil)
        }
    }
}
