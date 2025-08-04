package com.surgify.mobile.modules;

import android.Manifest;
import android.content.pm.PackageManager;
import android.hardware.biometrics.BiometricPrompt;
import android.os.Build;
import android.os.CancellationSignal;
import androidx.annotation.RequiresApi;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentActivity;

import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.bridge.WritableNativeMap;

public class BiometricModule extends ReactContextBaseJavaModule {
    
    private static final String MODULE_NAME = "BiometricModule";
    
    public BiometricModule(ReactApplicationContext reactContext) {
        super(reactContext);
    }

    @Override
    public String getName() {
        return MODULE_NAME;
    }

    @ReactMethod
    public void isAvailable(Promise promise) {
        try {
            WritableMap result = new WritableNativeMap();
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                PackageManager pm = getReactApplicationContext().getPackageManager();
                boolean hasFingerprint = pm.hasSystemFeature(PackageManager.FEATURE_FINGERPRINT);
                boolean hasFace = false;
                
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    hasFace = pm.hasSystemFeature(PackageManager.FEATURE_FACE);
                }
                
                boolean hasPermission = ContextCompat.checkSelfPermission(
                    getReactApplicationContext(), 
                    Manifest.permission.USE_FINGERPRINT
                ) == PackageManager.PERMISSION_GRANTED;
                
                result.putBoolean("isAvailable", (hasFingerprint || hasFace) && hasPermission);
                result.putBoolean("hasFingerprint", hasFingerprint);
                result.putBoolean("hasFace", hasFace);
                result.putBoolean("hasPermission", hasPermission);
                
                if (hasFingerprint && hasFace) {
                    result.putString("biometryType", "both");
                } else if (hasFingerprint) {
                    result.putString("biometryType", "fingerprint");
                } else if (hasFace) {
                    result.putString("biometryType", "face");
                } else {
                    result.putString("biometryType", "none");
                }
            } else {
                result.putBoolean("isAvailable", false);
                result.putString("biometryType", "none");
                result.putString("error", "Biometric authentication requires Android 6.0+");
            }
            
            promise.resolve(result);
        } catch (Exception e) {
            promise.reject("BIOMETRIC_CHECK_ERROR", e.getMessage(), e);
        }
    }

    @ReactMethod
    public void authenticate(String reason, Promise promise) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            authenticateWithBiometricPrompt(reason, promise);
        } else {
            promise.reject("UNSUPPORTED_VERSION", "BiometricPrompt requires Android 9.0+", null);
        }
    }

    @ReactMethod
    public void authenticateWithPasscode(String reason, Promise promise) {
        // For Android, this would typically involve device credentials
        // Implementation would depend on specific requirements
        promise.reject("NOT_IMPLEMENTED", "Passcode authentication not implemented", null);
    }

    @RequiresApi(api = Build.VERSION_CODES.P)
    private void authenticateWithBiometricPrompt(String reason, Promise promise) {
        try {
            FragmentActivity activity = (FragmentActivity) getCurrentActivity();
            if (activity == null) {
                promise.reject("NO_ACTIVITY", "No current activity available", null);
                return;
            }

            BiometricPrompt.Builder builder = new BiometricPrompt.Builder(getReactApplicationContext())
                .setTitle("Biometric Authentication")
                .setSubtitle(reason)
                .setDescription("Use your biometric credential to authenticate")
                .setNegativeButton("Cancel", getReactApplicationContext().getMainExecutor(), 
                    (dialog, which) -> {
                        promise.reject("USER_CANCELLED", "User cancelled authentication", null);
                    });

            BiometricPrompt biometricPrompt = builder.build();
            CancellationSignal cancellationSignal = new CancellationSignal();

            BiometricPrompt.AuthenticationCallback authCallback = new BiometricPrompt.AuthenticationCallback() {
                @Override
                public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult result) {
                    super.onAuthenticationSucceeded(result);
                    WritableMap response = new WritableNativeMap();
                    response.putBoolean("success", true);
                    response.putString("method", "biometric");
                    promise.resolve(response);
                }

                @Override
                public void onAuthenticationError(int errorCode, CharSequence errString) {
                    super.onAuthenticationError(errorCode, errString);
                    String errorType = getErrorType(errorCode);
                    promise.reject(errorType, errString.toString(), null);
                }

                @Override
                public void onAuthenticationFailed() {
                    super.onAuthenticationFailed();
                    promise.reject("AUTHENTICATION_FAILED", "Authentication failed", null);
                }
            };

            biometricPrompt.authenticate(cancellationSignal, 
                getReactApplicationContext().getMainExecutor(), authCallback);

        } catch (Exception e) {
            promise.reject("BIOMETRIC_ERROR", e.getMessage(), e);
        }
    }

    private String getErrorType(int errorCode) {
        switch (errorCode) {
            case BiometricPrompt.BIOMETRIC_ERROR_USER_CANCELED:
                return "USER_CANCELLED";
            case BiometricPrompt.BIOMETRIC_ERROR_NO_BIOMETRICS:
                return "BIOMETRY_NOT_ENROLLED";
            case BiometricPrompt.BIOMETRIC_ERROR_HW_NOT_PRESENT:
                return "BIOMETRY_NOT_AVAILABLE";
            case BiometricPrompt.BIOMETRIC_ERROR_HW_UNAVAILABLE:
                return "BIOMETRY_UNAVAILABLE";
            case BiometricPrompt.BIOMETRIC_ERROR_LOCKOUT:
                return "BIOMETRY_LOCKOUT";
            case BiometricPrompt.BIOMETRIC_ERROR_LOCKOUT_PERMANENT:
                return "BIOMETRY_LOCKOUT_PERMANENT";
            case BiometricPrompt.BIOMETRIC_ERROR_NO_SPACE:
                return "BIOMETRY_NO_SPACE";
            case BiometricPrompt.BIOMETRIC_ERROR_TIMEOUT:
                return "BIOMETRY_TIMEOUT";
            case BiometricPrompt.BIOMETRIC_ERROR_UNABLE_TO_PROCESS:
                return "BIOMETRY_UNABLE_TO_PROCESS";
            case BiometricPrompt.BIOMETRIC_ERROR_VENDOR:
                return "BIOMETRY_VENDOR_ERROR";
            default:
                return "UNKNOWN_ERROR";
        }
    }
}
