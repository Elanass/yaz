/**
 * Camera Screen - Native camera integration for medical imaging
 */

import React, {useState, useEffect, useRef} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Platform,
  SafeAreaView,
  StatusBar,
  Dimensions,
} from 'react-native';
import {RNCamera} from 'react-native-camera';
import Icon from 'react-native-vector-icons/MaterialIcons';
import DocumentPicker from 'react-native-document-picker';
import {check, request, PERMISSIONS, RESULTS} from 'react-native-permissions';

const {width, height} = Dimensions.get('window');

const CameraScreen: React.FC = () => {
  const [cameraPermission, setCameraPermission] = useState(false);
  const [flashMode, setFlashMode] = useState(RNCamera.Constants.FlashMode.off);
  const [cameraType, setCameraType] = useState(RNCamera.Constants.Type.back);
  const [isRecording, setIsRecording] = useState(false);
  const cameraRef = useRef<RNCamera>(null);

  useEffect(() => {
    checkCameraPermission();
  }, []);

  const checkCameraPermission = async () => {
    try {
      const permission = Platform.OS === 'ios' 
        ? PERMISSIONS.IOS.CAMERA 
        : PERMISSIONS.ANDROID.CAMERA;
      
      const result = await check(permission);
      
      if (result === RESULTS.GRANTED) {
        setCameraPermission(true);
      } else {
        requestCameraPermission();
      }
    } catch (error) {
      console.error('Permission check error:', error);
    }
  };

  const requestCameraPermission = async () => {
    try {
      const permission = Platform.OS === 'ios' 
        ? PERMISSIONS.IOS.CAMERA 
        : PERMISSIONS.ANDROID.CAMERA;
      
      const result = await request(permission);
      
      if (result === RESULTS.GRANTED) {
        setCameraPermission(true);
      } else {
        Alert.alert(
          'Camera Permission Required',
          'Please enable camera access in settings to capture medical images.',
          [
            {text: 'Cancel', style: 'cancel'},
            {text: 'Settings', onPress: () => {/* Open settings */}},
          ]
        );
      }
    } catch (error) {
      console.error('Permission request error:', error);
    }
  };

  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const options = {
          quality: 0.8,
          base64: false,
          exif: true,
          writeExif: true,
        };
        
        const data = await cameraRef.current.takePictureAsync(options);
        console.log('Picture taken:', data.uri);
        
        // Process and upload the image
        await processImage(data.uri, 'photo');
        
        Alert.alert('Success', 'Medical image captured successfully');
      } catch (error) {
        console.error('Take picture error:', error);
        Alert.alert('Error', 'Failed to capture image');
      }
    }
  };

  const recordVideo = async () => {
    if (cameraRef.current && !isRecording) {
      try {
        setIsRecording(true);
        
        const options = {
          quality: RNCamera.Constants.VideoQuality['720p'],
          maxDuration: 30, // 30 seconds max
          maxFileSize: 50 * 1024 * 1024, // 50MB max
        };
        
        const data = await cameraRef.current.recordAsync(options);
        console.log('Video recorded:', data.uri);
        
        // Process and upload the video
        await processImage(data.uri, 'video');
        
        Alert.alert('Success', 'Medical video recorded successfully');
      } catch (error) {
        console.error('Record video error:', error);
        Alert.alert('Error', 'Failed to record video');
      } finally {
        setIsRecording(false);
      }
    }
  };

  const stopRecording = () => {
    if (cameraRef.current && isRecording) {
      cameraRef.current.stopRecording();
    }
  };

  const processImage = async (uri: string, type: 'photo' | 'video') => {
    try {
      // Here you would implement the logic to:
      // 1. Apply medical imaging filters/enhancements
      // 2. Extract metadata
      // 3. Compress if needed
      // 4. Upload to Surgify platform
      // 5. Update case records
      
      console.log(`Processing ${type}:`, uri);
      
      // For now, just log the action
      // In a real implementation, this would integrate with your backend
    } catch (error) {
      console.error('Process image error:', error);
    }
  };

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.images, DocumentPicker.types.pdf],
        allowMultiSelection: true,
      });
      
      console.log('Documents picked:', result);
      
      // Process each selected document
      for (const doc of result) {
        await processImage(doc.uri, 'photo');
      }
      
      Alert.alert('Success', `${result.length} file(s) uploaded successfully`);
    } catch (error) {
      if (DocumentPicker.isCancel(error)) {
        // User cancelled
      } else {
        console.error('Document picker error:', error);
        Alert.alert('Error', 'Failed to pick documents');
      }
    }
  };

  const toggleFlash = () => {
    setFlashMode(current => 
      current === RNCamera.Constants.FlashMode.off 
        ? RNCamera.Constants.FlashMode.on 
        : RNCamera.Constants.FlashMode.off
    );
  };

  const toggleCamera = () => {
    setCameraType(current => 
      current === RNCamera.Constants.Type.back 
        ? RNCamera.Constants.Type.front 
        : RNCamera.Constants.Type.back
    );
  };

  if (!cameraPermission) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#000000" />
        <View style={styles.permissionContainer}>
          <Icon name="camera-alt" size={80} color="#6b7280" />
          <Text style={styles.permissionTitle}>Camera Access Required</Text>
          <Text style={styles.permissionText}>
            Enable camera access to capture medical images and videos for case documentation.
          </Text>
          <TouchableOpacity style={styles.permissionButton} onPress={requestCameraPermission}>
            <Text style={styles.permissionButtonText}>Enable Camera</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000000" />
      
      <RNCamera
        ref={cameraRef}
        style={styles.camera}
        type={cameraType}
        flashMode={flashMode}
        androidCameraPermissionOptions={{
          title: 'Permission to use camera',
          message: 'We need your permission to use your camera for medical imaging',
          buttonPositive: 'Ok',
          buttonNegative: 'Cancel',
        }}
        androidRecordAudioPermissionOptions={{
          title: 'Permission to use audio recording',
          message: 'We need your permission to use your audio for medical video recording',
          buttonPositive: 'Ok',
          buttonNegative: 'Cancel',
        }}>
        
        {/* Top Controls */}
        <View style={styles.topControls}>
          <TouchableOpacity style={styles.controlButton} onPress={toggleFlash}>
            <Icon 
              name={flashMode === RNCamera.Constants.FlashMode.on ? "flash-on" : "flash-off"} 
              size={24} 
              color="#ffffff" 
            />
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.controlButton} onPress={toggleCamera}>
            <Icon name="flip-camera-android" size={24} color="#ffffff" />
          </TouchableOpacity>
        </View>

        {/* Bottom Controls */}
        <View style={styles.bottomControls}>
          <TouchableOpacity style={styles.smallButton} onPress={pickDocument}>
            <Icon name="folder" size={24} color="#ffffff" />
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.captureButton, isRecording && styles.recordingButton]} 
            onPress={isRecording ? stopRecording : takePicture}
            onLongPress={recordVideo}>
            <View style={[styles.captureInner, isRecording && styles.recordingInner]} />
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.smallButton}>
            <Icon name="photo-library" size={24} color="#ffffff" />
          </TouchableOpacity>
        </View>
      </RNCamera>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#ffffff',
  },
  permissionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 24,
    marginBottom: 16,
    textAlign: 'center',
  },
  permissionText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  permissionButton: {
    backgroundColor: '#2563eb',
    borderRadius: 12,
    paddingHorizontal: 32,
    paddingVertical: 16,
  },
  permissionButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  camera: {
    flex: 1,
  },
  topControls: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 24,
  },
  controlButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  bottomControls: {
    position: 'absolute',
    bottom: 40,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  smallButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: 'rgba(255, 255, 255, 0.5)',
  },
  recordingButton: {
    borderColor: '#ef4444',
  },
  captureInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#ffffff',
  },
  recordingInner: {
    backgroundColor: '#ef4444',
    borderRadius: 8,
  },
});

export default CameraScreen;
