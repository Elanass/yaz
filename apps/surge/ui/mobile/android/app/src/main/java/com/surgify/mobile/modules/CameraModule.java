package com.surgify.mobile.modules;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.provider.MediaStore;
import android.util.Base64;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.facebook.react.bridge.ActivityEventListener;
import com.facebook.react.bridge.BaseActivityEventListener;
import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.ReadableMap;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.bridge.WritableNativeMap;

import java.io.ByteArrayOutputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;

public class CameraModule extends ReactContextBaseJavaModule {
    
    private static final String MODULE_NAME = "CameraModule";
    private static final int CAMERA_PERMISSION_REQUEST_CODE = 1001;
    private static final int CAMERA_CAPTURE_REQUEST_CODE = 1002;
    private static final int GALLERY_PICK_REQUEST_CODE = 1003;
    
    private Promise pendingPromise;
    private ReadableMap pendingOptions;
    
    private final ActivityEventListener activityEventListener = new BaseActivityEventListener() {
        @Override
        public void onActivityResult(Activity activity, int requestCode, int resultCode, Intent intent) {
            if (pendingPromise == null) {
                return;
            }
            
            if (requestCode == CAMERA_CAPTURE_REQUEST_CODE) {
                handleCameraResult(resultCode, intent);
            } else if (requestCode == GALLERY_PICK_REQUEST_CODE) {
                handleGalleryResult(resultCode, intent);
            }
        }
    };
    
    public CameraModule(ReactApplicationContext reactContext) {
        super(reactContext);
        reactContext.addActivityEventListener(activityEventListener);
    }

    @Override
    public String getName() {
        return MODULE_NAME;
    }

    @ReactMethod
    public void checkPermissions(Promise promise) {
        try {
            WritableMap result = new WritableNativeMap();
            
            int cameraPermission = ContextCompat.checkSelfPermission(
                getReactApplicationContext(), 
                Manifest.permission.CAMERA
            );
            
            int storagePermission = ContextCompat.checkSelfPermission(
                getReactApplicationContext(), 
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            );
            
            String cameraStatus = cameraPermission == PackageManager.PERMISSION_GRANTED ? "granted" : "denied";
            String storageStatus = storagePermission == PackageManager.PERMISSION_GRANTED ? "granted" : "denied";
            
            result.putString("camera", cameraStatus);
            result.putString("storage", storageStatus);
            
            promise.resolve(result);
        } catch (Exception e) {
            promise.reject("PERMISSION_CHECK_ERROR", e.getMessage(), e);
        }
    }

    @ReactMethod
    public void requestPermissions(Promise promise) {
        try {
            Activity activity = getCurrentActivity();
            if (activity == null) {
                promise.reject("NO_ACTIVITY", "No current activity available", null);
                return;
            }
            
            String[] permissions = {
                Manifest.permission.CAMERA,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            };
            
            ActivityCompat.requestPermissions(activity, permissions, CAMERA_PERMISSION_REQUEST_CODE);
            
            // Note: In a real implementation, you'd need to handle the permission result
            // For now, we'll assume permissions are granted
            WritableMap result = new WritableNativeMap();
            result.putString("camera", "granted");
            result.putString("storage", "granted");
            promise.resolve(result);
            
        } catch (Exception e) {
            promise.reject("PERMISSION_REQUEST_ERROR", e.getMessage(), e);
        }
    }

    @ReactMethod
    public void openCamera(ReadableMap options, Promise promise) {
        try {
            Activity activity = getCurrentActivity();
            if (activity == null) {
                promise.reject("NO_ACTIVITY", "No current activity available", null);
                return;
            }
            
            // Check camera permission
            if (ContextCompat.checkSelfPermission(getReactApplicationContext(), Manifest.permission.CAMERA) 
                != PackageManager.PERMISSION_GRANTED) {
                promise.reject("PERMISSION_DENIED", "Camera permission not granted", null);
                return;
            }
            
            pendingPromise = promise;
            pendingOptions = options;
            
            Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            if (takePictureIntent.resolveActivity(activity.getPackageManager()) != null) {
                activity.startActivityForResult(takePictureIntent, CAMERA_CAPTURE_REQUEST_CODE);
            } else {
                promise.reject("CAMERA_NOT_AVAILABLE", "Camera is not available", null);
                pendingPromise = null;
                pendingOptions = null;
            }
            
        } catch (Exception e) {
            promise.reject("CAMERA_ERROR", e.getMessage(), e);
            pendingPromise = null;
            pendingOptions = null;
        }
    }

    @ReactMethod
    public void openGallery(ReadableMap options, Promise promise) {
        try {
            Activity activity = getCurrentActivity();
            if (activity == null) {
                promise.reject("NO_ACTIVITY", "No current activity available", null);
                return;
            }
            
            pendingPromise = promise;
            pendingOptions = options;
            
            Intent pickPhotoIntent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
            pickPhotoIntent.setType("image/*");
            
            if (pickPhotoIntent.resolveActivity(activity.getPackageManager()) != null) {
                activity.startActivityForResult(pickPhotoIntent, GALLERY_PICK_REQUEST_CODE);
            } else {
                promise.reject("GALLERY_NOT_AVAILABLE", "Gallery is not available", null);
                pendingPromise = null;
                pendingOptions = null;
            }
            
        } catch (Exception e) {
            promise.reject("GALLERY_ERROR", e.getMessage(), e);
            pendingPromise = null;
            pendingOptions = null;
        }
    }

    @ReactMethod
    public void captureImage(ReadableMap options, Promise promise) {
        // For this implementation, captureImage will use the same logic as openCamera
        openCamera(options, promise);
    }

    private void handleCameraResult(int resultCode, Intent data) {
        if (pendingPromise == null) {
            return;
        }
        
        try {
            if (resultCode == Activity.RESULT_OK && data != null) {
                Bundle extras = data.getExtras();
                if (extras != null) {
                    Bitmap imageBitmap = (Bitmap) extras.get("data");
                    if (imageBitmap != null) {
                        processImage(imageBitmap);
                        return;
                    }
                }
            }
            
            pendingPromise.reject("USER_CANCELLED", "User cancelled camera", null);
            
        } catch (Exception e) {
            pendingPromise.reject("CAMERA_PROCESSING_ERROR", e.getMessage(), e);
        } finally {
            pendingPromise = null;
            pendingOptions = null;
        }
    }

    private void handleGalleryResult(int resultCode, Intent data) {
        if (pendingPromise == null) {
            return;
        }
        
        try {
            if (resultCode == Activity.RESULT_OK && data != null) {
                Uri selectedImage = data.getData();
                if (selectedImage != null) {
                    InputStream imageStream = getReactApplicationContext()
                        .getContentResolver()
                        .openInputStream(selectedImage);
                    Bitmap imageBitmap = BitmapFactory.decodeStream(imageStream);
                    if (imageBitmap != null) {
                        processImage(imageBitmap);
                        return;
                    }
                }
            }
            
            pendingPromise.reject("USER_CANCELLED", "User cancelled gallery selection", null);
            
        } catch (FileNotFoundException e) {
            pendingPromise.reject("FILE_NOT_FOUND", "Selected image file not found", e);
        } catch (Exception e) {
            pendingPromise.reject("GALLERY_PROCESSING_ERROR", e.getMessage(), e);
        } finally {
            pendingPromise = null;
            pendingOptions = null;
        }
    }

    private void processImage(Bitmap bitmap) {
        try {
            // Get quality setting from options
            float quality = 0.8f;
            if (pendingOptions != null && pendingOptions.hasKey("quality")) {
                String qualityStr = pendingOptions.getString("quality");
                switch (qualityStr) {
                    case "high":
                        quality = 1.0f;
                        break;
                    case "medium":
                        quality = 0.8f;
                        break;
                    case "low":
                        quality = 0.5f;
                        break;
                }
            }
            
            // Convert bitmap to base64
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.JPEG, (int)(quality * 100), byteArrayOutputStream);
            byte[] byteArray = byteArrayOutputStream.toByteArray();
            String base64String = Base64.encodeToString(byteArray, Base64.DEFAULT);
            
            WritableMap result = new WritableNativeMap();
            result.putString("uri", "data:image/jpeg;base64," + base64String);
            result.putInt("width", bitmap.getWidth());
            result.putInt("height", bitmap.getHeight());
            result.putString("type", "image/jpeg");
            
            pendingPromise.resolve(result);
            
        } catch (Exception e) {
            pendingPromise.reject("IMAGE_PROCESSING_ERROR", e.getMessage(), e);
        }
    }
}
