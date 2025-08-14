const {getDefaultConfig, mergeConfig} = require('@react-native/metro-config');

/**
 * Metro configuration
 * https://reactnative.dev/docs/metro
 *
 * @type {import('metro-config').MetroConfig}
 */
const config = {
  resolver: {
    alias: {
      '@': './src',
      '@screens': './src/screens',
      '@services': './src/services',
      '@components': './src/components',
      '@utils': './src/utils',
      '@types': './src/types',
    },
  },
  transformer: {
    getTransformCacheKeyFn() {
      return () =>
        crypto
          .createHash('md5')
          .update(fs.readFileSync(__filename))
          .digest('hex');
    },
  },
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);
