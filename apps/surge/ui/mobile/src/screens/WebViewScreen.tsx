/**
 * WebView Screen - Main interface to Surgify web platform
 */

import React, {useState, useRef, useEffect} from 'react';
import {
  View,
  StyleSheet,
  Alert,
  RefreshControl,
  StatusBar,
  Platform,
  SafeAreaView,
} from 'react-native';
import {WebView} from 'react-native-webview';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useFocusEffect} from '@react-navigation/native';

interface WebViewScreenProps {
  route: {
    params: {
      url: string;
    };
  };
}

const WebViewScreen: React.FC<WebViewScreenProps> = ({route}) => {
  const {url} = route.params;
  const webViewRef = useRef<WebView>(null);
  const [loading, setLoading] = useState(true);
  const [canGoBack, setCanGoBack] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useFocusEffect(
    React.useCallback(() => {
      // Refresh webview when screen comes into focus
      if (webViewRef.current) {
        webViewRef.current.reload();
      }
    }, []),
  );

  const handleNavigationStateChange = (navState: any) => {
    setCanGoBack(navState.canGoBack);
    setLoading(navState.loading);
  };

  const handleError = (syntheticEvent: any) => {
    const {nativeEvent} = syntheticEvent;
    console.warn('WebView error: ', nativeEvent);
    Alert.alert(
      'Connection Error',
      'Unable to connect to Surgify platform. Please check your internet connection.',
      [
        {text: 'Retry', onPress: () => webViewRef.current?.reload()},
        {text: 'OK', style: 'cancel'},
      ],
    );
  };

  const handleMessage = (event: any) => {
    try {
      const message = JSON.parse(event.nativeEvent.data);
      
      switch (message.type) {
        case 'BIOMETRIC_AUTH':
          // Handle biometric authentication request
          handleBiometricAuth(message.payload);
          break;
        case 'CAMERA_ACCESS':
          // Handle camera access request
          handleCameraAccess(message.payload);
          break;
        case 'FILE_UPLOAD':
          // Handle file upload request
          handleFileUpload(message.payload);
          break;
        case 'NOTIFICATION':
          // Handle notification request
          handleNotification(message.payload);
          break;
        default:
          console.log('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Error parsing webview message:', error);
    }
  };

  const handleBiometricAuth = async (payload: any) => {
    // Implementation for biometric authentication
    console.log('Biometric auth requested:', payload);
  };

  const handleCameraAccess = async (payload: any) => {
    // Implementation for camera access
    console.log('Camera access requested:', payload);
  };

  const handleFileUpload = async (payload: any) => {
    // Implementation for file upload
    console.log('File upload requested:', payload);
  };

  const handleNotification = async (payload: any) => {
    // Implementation for notifications
    console.log('Notification requested:', payload);
  };

  const injectedJavaScript = `
    // Inject native bridge for communication
    window.SurgifyNative = {
      requestBiometric: function(payload) {
        window.ReactNativeWebView.postMessage(JSON.stringify({
          type: 'BIOMETRIC_AUTH',
          payload: payload
        }));
      },
      requestCamera: function(payload) {
        window.ReactNativeWebView.postMessage(JSON.stringify({
          type: 'CAMERA_ACCESS',
          payload: payload
        }));
      },
      uploadFile: function(payload) {
        window.ReactNativeWebView.postMessage(JSON.stringify({
          type: 'FILE_UPLOAD',
          payload: payload
        }));
      },
      showNotification: function(payload) {
        window.ReactNativeWebView.postMessage(JSON.stringify({
          type: 'NOTIFICATION',
          payload: payload
        }));
      },
      platform: '${Platform.OS}',
      version: '${Platform.Version}'
    };
    
    // Add mobile-specific styles
    const style = document.createElement('style');
    style.textContent = \`
      body {
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        user-select: none;
      }
      .mobile-hidden {
        display: none !important;
      }
      .mobile-optimized {
        touch-action: manipulation;
      }
    \`;
    document.head.appendChild(style);
    
    true; // Required for injected scripts
  `;

  const onRefresh = () => {
    setRefreshing(true);
    webViewRef.current?.reload();
    setTimeout(() => setRefreshing(false), 1000);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      <View style={styles.webviewContainer}>
        <WebView
          ref={webViewRef}
          source={{uri: url}}
          style={styles.webview}
          onNavigationStateChange={handleNavigationStateChange}
          onError={handleError}
          onMessage={handleMessage}
          injectedJavaScript={injectedJavaScript}
          javaScriptEnabled={true}
          domStorageEnabled={true}
          allowsInlineMediaPlayback={true}
          mediaPlaybackRequiresUserAction={false}
          mixedContentMode="compatibility"
          pullToRefreshEnabled={true}
          bounces={true}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          userAgent={`SurgifyMobile/${Platform.OS} (${Platform.Version})`}
        />
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  webviewContainer: {
    flex: 1,
  },
  webview: {
    flex: 1,
  },
});

export default WebViewScreen;
