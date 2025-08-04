/**
 * Surgify Mobile App Entry Point
 * Thin native layer for Android and iOS
 */

import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StatusBar,
  Alert,
  Platform,
  StyleSheet,
  SafeAreaView,
} from 'react-native';
import {NavigationContainer} from '@react-navigation/native';
import {createStackNavigator} from '@react-navigation/stack';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';
import DeviceInfo from 'react-native-device-info';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import screens
import WebViewScreen from './src/screens/WebViewScreen';
import AuthScreen from './src/screens/AuthScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import CameraScreen from './src/screens/CameraScreen';
import OfflineScreen from './src/screens/OfflineScreen';

// Import services
import AuthService from './src/services/AuthService';
import NetworkService from './src/services/NetworkService';
import BiometricService from './src/services/BiometricService';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Main Tab Navigator
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        tabBarIcon: ({focused, color, size}) => {
          let iconName;

          if (route.name === 'Platform') {
            iconName = 'medical-services';
          } else if (route.name === 'Workstation') {
            iconName = 'work';
          } else if (route.name === 'Camera') {
            iconName = 'camera-alt';
          } else if (route.name === 'Settings') {
            iconName = 'settings';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2563eb',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          backgroundColor: 'white',
          borderTopWidth: 1,
          borderTopColor: '#e5e7eb',
          paddingBottom: Platform.OS === 'ios' ? 20 : 5,
          height: Platform.OS === 'ios' ? 90 : 60,
        },
        headerShown: false,
      })}>
      <Tab.Screen 
        name="Platform" 
        component={WebViewScreen}
        initialParams={{url: 'https://surgify.local'}}
      />
      <Tab.Screen 
        name="Workstation" 
        component={WebViewScreen}
        initialParams={{url: 'https://surgify.local/workstation'}}
      />
      <Tab.Screen name="Camera" component={CameraScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

// Main App Component
function App(): JSX.Element {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isOnline, setIsOnline] = useState(true);
  const [deviceInfo, setDeviceInfo] = useState({});

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Get device information
      const info = {
        deviceId: await DeviceInfo.getUniqueId(),
        systemName: DeviceInfo.getSystemName(),
        systemVersion: DeviceInfo.getSystemVersion(),
        appVersion: DeviceInfo.getVersion(),
        buildNumber: DeviceInfo.getBuildNumber(),
        brand: await DeviceInfo.getBrand(),
        model: await DeviceInfo.getModel(),
      };
      setDeviceInfo(info);

      // Check network connectivity
      const networkStatus = await NetworkService.checkConnectivity();
      setIsOnline(networkStatus);

      // Check authentication status
      const authStatus = await AuthService.isAuthenticated();
      setIsAuthenticated(authStatus);

      // Initialize biometric authentication if available
      const biometricAvailable = await BiometricService.isAvailable();
      if (biometricAvailable && authStatus) {
        await BiometricService.initialize();
      }

      setIsLoading(false);
    } catch (error) {
      console.error('App initialization error:', error);
      Alert.alert('Initialization Error', 'Failed to initialize app');
      setIsLoading(false);
    }
  };

  const handleLogin = async (credentials) => {
    try {
      const result = await AuthService.login(credentials);
      if (result.success) {
        setIsAuthenticated(true);
        
        // Setup biometric authentication
        const biometricAvailable = await BiometricService.isAvailable();
        if (biometricAvailable) {
          Alert.alert(
            'Biometric Authentication',
            'Enable biometric login for faster access?',
            [
              {text: 'Later', style: 'cancel'},
              {
                text: 'Enable',
                onPress: () => BiometricService.setup(credentials),
              },
            ],
          );
        }
      }
    } catch (error) {
      Alert.alert('Login Failed', error.message);
    }
  };

  const handleLogout = async () => {
    try {
      await AuthService.logout();
      await BiometricService.clear();
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
        <View style={styles.loadingContainer}>
          <Icon name="medical-services" size={60} color="#2563eb" />
          <Text style={styles.loadingText}>Surgify</Text>
          <Text style={styles.loadingSubtext}>Loading...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!isOnline) {
    return <OfflineScreen onRetry={initializeApp} />;
  }

  return (
    <NavigationContainer>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      <Stack.Navigator screenOptions={{headerShown: false}}>
        {isAuthenticated ? (
          <Stack.Screen name="Main" component={MainTabs} />
        ) : (
          <Stack.Screen name="Auth">
            {props => (
              <AuthScreen {...props} onLogin={handleLogin} deviceInfo={deviceInfo} />
            )}
          </Stack.Screen>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  loadingText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
  },
  loadingSubtext: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 8,
  },
});

export default App;
