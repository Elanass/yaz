import UIKit
import React

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?
    var bridge: RCTBridge!

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        // Initialize React Native bridge
        bridge = RCTBridge(delegate: self, launchOptions: launchOptions)
        
        // Create root view controller
        let rootViewController = UIViewController()
        rootViewController.view = RCTRootView(
            bridge: bridge,
            moduleName: "SurgifyMobile",
            initialProperties: nil
        )
        
        // Setup window
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = rootViewController
        window?.makeKeyAndVisible()
        
        return true
    }

    // MARK: UISceneSession Lifecycle (iOS 13+)
    @available(iOS 13.0, *)
    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
    }

    @available(iOS 13.0, *)
    func application(_ application: UIApplication, didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {
        // Called when the user discards a scene session.
    }
}

// MARK: - RCTBridgeDelegate
extension AppDelegate: RCTBridgeDelegate {
    
    func sourceURL(for bridge: RCTBridge!) -> URL! {
        #if DEBUG
        return RCTBundleURLProvider.sharedSettings().jsBundleURL(forBundleRoot: "index", fallbackResource: nil)
        #else
        return Bundle.main.url(forResource: "main", withExtension: "jsbundle")
        #endif
    }
}
