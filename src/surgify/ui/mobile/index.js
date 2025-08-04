/**
 * Surgify Mobile App Entry Point
 */

import React from 'react';
import { AppRegistry } from 'react-native';
import App from './App';
import { name as appName } from '../package.json';

// Register the main application component
AppRegistry.registerComponent(appName, () => App);

// Export for Metro bundler
export default App;
