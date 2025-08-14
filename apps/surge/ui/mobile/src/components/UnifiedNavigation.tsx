/**
 * Enhanced Unified Navigation Component for React Native
 * Matches web navigation structure with state-of-the-art UI
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import { TOKENS } from '../styles/tokens';

interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  route: string;
}

const navigationItems: NavigationItem[] = [
  { id: 'landing', label: 'Dashboard', icon: 'home', route: '/' },
  { id: 'explorer', label: 'Explorer', icon: 'search', route: '/islands/indexing' },
  { id: 'cases', label: 'Cases', icon: 'briefcase', route: '/cases' },
  { id: 'datasets', label: 'Datasets', icon: 'database', route: '/datasets' },
  { id: 'settings', label: 'Settings', icon: 'cog', route: '/settings' },
];

interface UnifiedNavigationProps {
  activeRoute: string;
  onNavigate: (route: string, id: string) => void;
}

export const UnifiedNavigation: React.FC<UnifiedNavigationProps> = ({
  activeRoute,
  onNavigate,
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.backdrop} />
      
      {navigationItems.map((item) => {
        const isActive = activeRoute === item.route || activeRoute === item.id;
        
        return (
          <TouchableOpacity
            key={item.id}
            style={[
              styles.navItem, 
              isActive && styles.activeNavItem
            ]}
            onPress={() => onNavigate(item.route, item.id)}
            accessibilityLabel={item.label}
            accessibilityRole="button"
            activeOpacity={0.7}
          >
            {/* Active Indicator */}
            {isActive && <View style={styles.activeIndicator} />}
            
            {/* Icon Container */}
            <View style={[
              styles.iconContainer,
              isActive && styles.activeIconContainer
            ]}>
              <Icon
                name={item.icon}
                size={20}
                color={isActive ? TOKENS.brand : TOKENS.muted}
              />
            </View>
            
            {/* Label */}
            <Text style={[
              styles.navLabel,
              isActive && styles.activeNavLabel
            ]}>
              {item.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: TOKENS.bg,
    borderTopWidth: 1,
    borderTopColor: '#1c2230',
    paddingVertical: TOKENS.spacing[2],
    paddingHorizontal: TOKENS.spacing[3],
    position: 'relative',
    // Safe area handling for modern devices
    paddingBottom: TOKENS.spacing[4] + 20, // Extra padding for home indicator
  },
  
  backdrop: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: TOKENS.bg + 'F5', // 96% opacity
    // Note: backdropFilter requires react-native-blur or similar
  },
  
  navItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: TOKENS.spacing[2],
    paddingHorizontal: TOKENS.spacing[1],
    borderRadius: TOKENS.radius,
    position: 'relative',
    minHeight: 56,
  },
  
  activeNavItem: {
    backgroundColor: TOKENS.brand + '15', // 8% opacity
  },
  
  activeIndicator: {
    position: 'absolute',
    top: -TOKENS.spacing[2],
    left: '50%',
    marginLeft: -16,
    width: 32,
    height: 3,
    backgroundColor: TOKENS.brand,
    borderRadius: 2,
  },
  
  iconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: TOKENS.spacing[1],
    backgroundColor: 'transparent',
  },
  
  activeIconContainer: {
    backgroundColor: TOKENS.brand + '20', // 12% opacity
  },
  
  navLabel: {
    fontSize: 11,
    fontWeight: '500',
    color: TOKENS.muted,
    fontFamily: TOKENS.fontUI,
    textAlign: 'center',
  },
  
  activeNavLabel: {
    color: TOKENS.brand,
    fontWeight: '600',
  },
});

export default UnifiedNavigation;
