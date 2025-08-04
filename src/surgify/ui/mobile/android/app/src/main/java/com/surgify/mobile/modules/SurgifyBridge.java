package com.surgify.mobile.modules;

import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;
import android.provider.Settings;
import android.telephony.TelephonyManager;
import android.hardware.fingerprint.FingerprintManager;

import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.ReadableArray;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.bridge.WritableNativeMap;

import java.io.File;
import java.util.Arrays;
import java.util.List;

import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

import java.net.URL;
import java.security.cert.Certificate;
import java.security.cert.X509Certificate;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Set;

public class SurgifyBridge extends ReactContextBaseJavaModule {
    
    private static final String MODULE_NAME = "SurgifyBridge";
    private Set<String> certificatePins = new HashSet<>();
    
    public SurgifyBridge(ReactApplicationContext reactContext) {
        super(reactContext);
    }

    @Override
    public String getName() {
        return MODULE_NAME;
    }

    @ReactMethod
    public void getDeviceInfo(Promise promise) {
        try {
            WritableMap deviceInfo = new WritableNativeMap();
            
            deviceInfo.putString("platform", "android");
            deviceInfo.putString("model", Build.MODEL);
            deviceInfo.putString("manufacturer", Build.MANUFACTURER);
            deviceInfo.putString("brand", Build.BRAND);
            deviceInfo.putString("systemName", "Android");
            deviceInfo.putString("systemVersion", Build.VERSION.RELEASE);
            deviceInfo.putInt("apiLevel", Build.VERSION.SDK_INT);
            deviceInfo.putString("androidId", Settings.Secure.getString(
                getReactApplicationContext().getContentResolver(),
                Settings.Secure.ANDROID_ID
            ));
            deviceInfo.putBoolean("isEmulator", isEmulator());
            
            promise.resolve(deviceInfo);
        } catch (Exception e) {
            promise.reject("DEVICE_INFO_ERROR", e.getMessage(), e);
        }
    }

    @ReactMethod
    public void enableScreenRecordingProtection(Promise promise) {
        try {
            // Note: Android screen recording protection requires setting FLAG_SECURE
            // This would typically be done at the Activity level
            // For React Native, you'd need to modify the MainActivity
            getCurrentActivity().getWindow().setFlags(
                android.view.WindowManager.LayoutParams.FLAG_SECURE,
                android.view.WindowManager.LayoutParams.FLAG_SECURE
            );
            promise.resolve(true);
        } catch (Exception e) {
            promise.reject("SCREEN_PROTECTION_ERROR", e.getMessage(), e);
        }
    }

    @ReactMethod
    public void checkRootStatus(Promise promise) {
        try {
            WritableMap result = new WritableNativeMap();
            result.putBoolean("isRooted", isDeviceRooted());
            promise.resolve(result);
        } catch (Exception e) {
            promise.reject("ROOT_CHECK_ERROR", e.getMessage(), e);
        }
    }

    @ReactMethod
    public void enableCertificatePinning(ReadableArray pins, Promise promise) {
        try {
            certificatePins.clear();
            for (int i = 0; i < pins.size(); i++) {
                certificatePins.add(pins.getString(i));
            }
            promise.resolve(true);
        } catch (Exception e) {
            promise.reject("CERT_PINNING_ERROR", e.getMessage(), e);
        }
    }

    @ReactMethod
    public void validateNetworkConnection(String urlString, Promise promise) {
        new Thread(() -> {
            try {
                URL url = new URL(urlString);
                HttpsURLConnection connection = (HttpsURLConnection) url.openConnection();
                
                // Set connection properties
                connection.setRequestMethod("GET");
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(10000);
                
                // Validate certificate pinning if configured
                if (!certificatePins.isEmpty()) {
                    Certificate[] certificates = connection.getServerCertificates();
                    boolean pinValid = false;
                    
                    for (Certificate cert : certificates) {
                        if (cert instanceof X509Certificate) {
                            String pin = getCertificatePin((X509Certificate) cert);
                            if (certificatePins.contains(pin)) {
                                pinValid = true;
                                break;
                            }
                        }
                    }
                    
                    if (!pinValid) {
                        promise.reject("CERT_PIN_MISMATCH", "Certificate pinning validation failed", null);
                        return;
                    }
                }
                
                int responseCode = connection.getResponseCode();
                
                WritableMap result = new WritableNativeMap();
                result.putBoolean("isValid", responseCode == 200);
                result.putInt("statusCode", responseCode);
                
                WritableMap headers = new WritableNativeMap();
                for (String key : connection.getHeaderFields().keySet()) {
                    if (key != null) {
                        headers.putString(key, connection.getHeaderField(key));
                    }
                }
                result.putMap("headers", headers);
                
                promise.resolve(result);
                
            } catch (Exception e) {
                promise.reject("NETWORK_ERROR", e.getMessage(), e);
            }
        }).start();
    }

    @ReactMethod
    public void secureStoreData(String key, String data, Promise promise) {
        try {
            // Use Android Keystore for secure storage
            SecureStorage.store(getReactApplicationContext(), key, data);
            promise.resolve(true);
        } catch (Exception e) {
            promise.reject("SECURE_STORAGE_ERROR", e.getMessage(), e);
        }
    }

    @ReactMethod
    public void secureRetrieveData(String key, Promise promise) {
        try {
            String data = SecureStorage.retrieve(getReactApplicationContext(), key);
            if (data != null) {
                promise.resolve(data);
            } else {
                promise.reject("DATA_NOT_FOUND", "No data found for key: " + key, null);
            }
        } catch (Exception e) {
            promise.reject("SECURE_STORAGE_ERROR", e.getMessage(), e);
        }
    }

    // Private helper methods
    private boolean isEmulator() {
        return Build.FINGERPRINT.startsWith("generic")
                || Build.FINGERPRINT.startsWith("unknown")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.MODEL.contains("Android SDK built for x86")
                || Build.MANUFACTURER.contains("Genymotion")
                || (Build.BRAND.startsWith("generic") && Build.DEVICE.startsWith("generic"))
                || "google_sdk".equals(Build.PRODUCT);
    }

    private boolean isDeviceRooted() {
        // Check for common root indicators
        String[] rootPaths = {
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su"
        };

        for (String path : rootPaths) {
            if (new File(path).exists()) {
                return true;
            }
        }

        // Check for root management apps
        String[] rootApps = {
            "com.noshufou.android.su",
            "com.noshufou.android.su.elite",
            "eu.chainfire.supersu",
            "com.koushikdutta.superuser",
            "com.thirdparty.superuser",
            "com.yellowes.su"
        };

        PackageManager pm = getReactApplicationContext().getPackageManager();
        for (String app : rootApps) {
            try {
                pm.getPackageInfo(app, 0);
                return true;
            } catch (PackageManager.NameNotFoundException e) {
                // Package not found, continue checking
            }
        }

        // Check for dangerous properties
        String buildTags = Build.TAGS;
        if (buildTags != null && buildTags.contains("test-keys")) {
            return true;
        }

        return false;
    }

    private String getCertificatePin(X509Certificate certificate) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] publicKeyBytes = certificate.getPublicKey().getEncoded();
            byte[] hash = digest.digest(publicKeyBytes);
            
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return "";
        }
    }
}
