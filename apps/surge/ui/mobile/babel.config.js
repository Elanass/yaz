module.exports = {
  presets: ['module:metro-react-native-babel-preset'],
  plugins: [
    [
      'module-resolver',
      {
        root: ['./src'],
        extensions: ['.ios.js', '.android.js', '.js', '.ts', '.tsx', '.json'],
        alias: {
          '@': './src',
          '@screens': './src/screens',
          '@services': './src/services',
          '@components': './src/components',
          '@utils': './src/utils',
          '@types': './src/types',
        },
      },
    ],
  ],
};
