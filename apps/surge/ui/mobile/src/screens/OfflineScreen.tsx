/**
 * Offline Screen - Displayed when no internet connection
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  StatusBar,
  Animated,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import NetworkService from '../services/NetworkService';

interface OfflineScreenProps {
  onRetry: () => void;
}

const OfflineScreen: React.FC<OfflineScreenProps> = ({onRetry}) => {
  const [isRetrying, setIsRetrying] = useState(false);
  const [pulseAnim] = useState(new Animated.Value(1));

  useEffect(() => {
    startPulseAnimation();
  }, []);

  const startPulseAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.2,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const handleRetry = async () => {
    setIsRetrying(true);
    
    try {
      const isConnected = await NetworkService.checkConnectivity();
      
      if (isConnected) {
        onRetry();
      } else {
        // Still offline, show message
        setTimeout(() => {
          setIsRetrying(false);
        }, 2000);
      }
    } catch (error) {
      console.error('Retry connection error:', error);
      setIsRetrying(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      
      <View style={styles.content}>
        {/* Animated Icon */}
        <Animated.View style={[styles.iconContainer, {transform: [{scale: pulseAnim}]}]}>
          <Icon name="cloud-off" size={80} color="#6b7280" />
        </Animated.View>

        {/* Title */}
        <Text style={styles.title}>No Internet Connection</Text>
        
        {/* Description */}
        <Text style={styles.description}>
          Please check your internet connection and try again. Some features may be available offline.
        </Text>

        {/* Retry Button */}
        <TouchableOpacity 
          style={[styles.retryButton, isRetrying && styles.retryButtonDisabled]} 
          onPress={handleRetry}
          disabled={isRetrying}
        >
          <Icon 
            name={isRetrying ? "hourglass-empty" : "refresh"} 
            size={24} 
            color="#ffffff" 
            style={styles.retryIcon}
          />
          <Text style={styles.retryText}>
            {isRetrying ? 'Checking...' : 'Try Again'}
          </Text>
        </TouchableOpacity>

        {/* Offline Features */}
        <View style={styles.offlineFeatures}>
          <Text style={styles.offlineFeaturesTitle}>Available Offline:</Text>
          
          <View style={styles.featureItem}>
            <Icon name="visibility" size={20} color="#2563eb" />
            <Text style={styles.featureText}>View cached cases</Text>
          </View>
          
          <View style={styles.featureItem}>
            <Icon name="camera-alt" size={20} color="#2563eb" />
            <Text style={styles.featureText}>Capture images (syncs when online)</Text>
          </View>
          
          <View style={styles.featureItem}>
            <Icon name="settings" size={20} color="#2563eb" />
            <Text style={styles.featureText}>App settings</Text>
          </View>
        </View>

        {/* Network Tips */}
        <View style={styles.tips}>
          <Text style={styles.tipsTitle}>Troubleshooting:</Text>
          <Text style={styles.tipText}>• Check if WiFi or mobile data is enabled</Text>
          <Text style={styles.tipText}>• Try moving to a different location</Text>
          <Text style={styles.tipText}>• Restart your device if problems persist</Text>
        </View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  iconContainer: {
    marginBottom: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 16,
  },
  description: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  retryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#2563eb',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
    marginBottom: 48,
  },
  retryButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  retryIcon: {
    marginRight: 8,
  },
  retryText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  offlineFeatures: {
    width: '100%',
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
  },
  offlineFeaturesTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 16,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  featureText: {
    fontSize: 16,
    color: '#6b7280',
    marginLeft: 12,
  },
  tips: {
    width: '100%',
    backgroundColor: '#fef3c7',
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: '#f59e0b',
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#92400e',
    marginBottom: 12,
  },
  tipText: {
    fontSize: 14,
    color: '#92400e',
    marginBottom: 4,
    lineHeight: 20,
  },
});

export default OfflineScreen;
