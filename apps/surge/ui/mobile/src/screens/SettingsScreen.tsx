/**
 * Settings Screen - App configuration and preferences
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Switch,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import DeviceInfo from 'react-native-device-info';
import AuthService from '../services/AuthService';
import BiometricService from '../services/BiometricService';
import NetworkService from '../services/NetworkService';

const SettingsScreen: React.FC = () => {
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [biometricAvailable, setBiometricAvailable] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [offlineMode, setOfflineMode] = useState(false);
  const [deviceInfo, setDeviceInfo] = useState<any>({});
  const [networkQuality, setNetworkQuality] = useState<string>('checking');

  useEffect(() => {
    loadSettings();
    getDeviceInfo();
    checkNetworkQuality();
  }, []);

  const loadSettings = async () => {
    try {
      const biometricSetup = await BiometricService.isSetup();
      const available = await BiometricService.isAvailable();
      
      setBiometricEnabled(biometricSetup);
      setBiometricAvailable(available);
    } catch (error) {
      console.error('Load settings error:', error);
    }
  };

  const getDeviceInfo = async () => {
    try {
      const info = {
        deviceId: await DeviceInfo.getUniqueId(),
        systemName: DeviceInfo.getSystemName(),
        systemVersion: DeviceInfo.getSystemVersion(),
        appVersion: DeviceInfo.getVersion(),
        buildNumber: DeviceInfo.getBuildNumber(),
        brand: await DeviceInfo.getBrand(),
        model: await DeviceInfo.getModel(),
        batteryLevel: await DeviceInfo.getBatteryLevel(),
        isEmulator: await DeviceInfo.isEmulator(),
      };
      setDeviceInfo(info);
    } catch (error) {
      console.error('Get device info error:', error);
    }
  };

  const checkNetworkQuality = async () => {
    try {
      const quality = await NetworkService.getNetworkQuality();
      setNetworkQuality(quality);
    } catch (error) {
      console.error('Network quality check error:', error);
      setNetworkQuality('unknown');
    }
  };

  const handleBiometricToggle = async (value: boolean) => {
    if (value) {
      // Enable biometric authentication
      const credentials = await AuthService.getStoredCredentials();
      if (credentials) {
        const success = await BiometricService.setup(credentials);
        setBiometricEnabled(success);
      } else {
        Alert.alert(
          'Credentials Required',
          'Please log in again to enable biometric authentication.'
        );
      }
    } else {
      // Disable biometric authentication
      await BiometricService.disable();
      setBiometricEnabled(false);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to log out?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await AuthService.logout();
            // Navigation will be handled by the parent component
          },
        },
      ]
    );
  };

  const handleClearCache = () => {
    Alert.alert(
      'Clear Cache',
      'This will clear all cached data. Continue?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Clear',
          style: 'destructive',
          onPress: () => {
            // Implement cache clearing logic
            Alert.alert('Success', 'Cache cleared successfully');
          },
        },
      ]
    );
  };

  const getNetworkQualityColor = () => {
    switch (networkQuality) {
      case 'excellent': return '#10b981';
      case 'good': return '#3b82f6';
      case 'fair': return '#f59e0b';
      case 'poor': return '#ef4444';
      case 'offline': return '#6b7280';
      default: return '#6b7280';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Settings</Text>
        </View>

        {/* Security Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Security</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingLeft}>
              <Icon name="fingerprint" size={24} color="#2563eb" />
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Biometric Authentication</Text>
                <Text style={styles.settingSubtitle}>
                  {biometricAvailable ? 'Use biometric for quick access' : 'Not available on this device'}
                </Text>
              </View>
            </View>
            <Switch
              value={biometricEnabled}
              onValueChange={handleBiometricToggle}
              disabled={!biometricAvailable}
              trackColor={{false: '#e5e7eb', true: '#93c5fd'}}
              thumbColor={biometricEnabled ? '#2563eb' : '#f4f3f4'}
            />
          </View>
        </View>

        {/* Notifications Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notifications</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingLeft}>
              <Icon name="notifications" size={24} color="#2563eb" />
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Push Notifications</Text>
                <Text style={styles.settingSubtitle}>Receive alerts for case updates</Text>
              </View>
            </View>
            <Switch
              value={notifications}
              onValueChange={setNotifications}
              trackColor={{false: '#e5e7eb', true: '#93c5fd'}}
              thumbColor={notifications ? '#2563eb' : '#f4f3f4'}
            />
          </View>
        </View>

        {/* Data Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Data & Storage</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingLeft}>
              <Icon name="cloud-off" size={24} color="#2563eb" />
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Offline Mode</Text>
                <Text style={styles.settingSubtitle}>Cache data for offline access</Text>
              </View>
            </View>
            <Switch
              value={offlineMode}
              onValueChange={setOfflineMode}
              trackColor={{false: '#e5e7eb', true: '#93c5fd'}}
              thumbColor={offlineMode ? '#2563eb' : '#f4f3f4'}
            />
          </View>

          <TouchableOpacity style={styles.settingItem} onPress={handleClearCache}>
            <View style={styles.settingLeft}>
              <Icon name="delete-sweep" size={24} color="#2563eb" />
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Clear Cache</Text>
                <Text style={styles.settingSubtitle}>Free up storage space</Text>
              </View>
            </View>
            <Icon name="chevron-right" size={24} color="#9ca3af" />
          </TouchableOpacity>
        </View>

        {/* Network Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Network</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingLeft}>
              <Icon name="network-check" size={24} color="#2563eb" />
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Connection Quality</Text>
                <Text style={[styles.settingSubtitle, {color: getNetworkQualityColor()}]}>
                  {networkQuality.charAt(0).toUpperCase() + networkQuality.slice(1)}
                </Text>
              </View>
            </View>
            <TouchableOpacity onPress={checkNetworkQuality}>
              <Icon name="refresh" size={24} color="#9ca3af" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Device Info Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Device Information</Text>
          
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Device</Text>
            <Text style={styles.infoValue}>{deviceInfo.brand} {deviceInfo.model}</Text>
          </View>
          
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>System</Text>
            <Text style={styles.infoValue}>{deviceInfo.systemName} {deviceInfo.systemVersion}</Text>
          </View>
          
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>App Version</Text>
            <Text style={styles.infoValue}>{deviceInfo.appVersion} ({deviceInfo.buildNumber})</Text>
          </View>
          
          {deviceInfo.batteryLevel && (
            <View style={styles.infoItem}>
              <Text style={styles.infoLabel}>Battery</Text>
              <Text style={styles.infoValue}>{Math.round(deviceInfo.batteryLevel * 100)}%</Text>
            </View>
          )}
        </View>

        {/* Account Section */}
        <View style={styles.section}>
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Icon name="logout" size={24} color="#ffffff" />
            <Text style={styles.logoutText}>Logout</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 24,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  section: {
    marginTop: 24,
    backgroundColor: '#ffffff',
    paddingVertical: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
    paddingHorizontal: 24,
    marginBottom: 16,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingText: {
    marginLeft: 16,
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1f2937',
  },
  settingSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  infoLabel: {
    fontSize: 16,
    color: '#374151',
  },
  infoValue: {
    fontSize: 16,
    color: '#6b7280',
    fontWeight: '500',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ef4444',
    marginHorizontal: 24,
    marginVertical: 16,
    paddingVertical: 16,
    borderRadius: 12,
  },
  logoutText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});

export default SettingsScreen;
