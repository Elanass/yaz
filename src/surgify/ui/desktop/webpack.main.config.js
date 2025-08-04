const path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/main/main.ts',
  target: 'electron-main',
  module: {
    rules: [
      {
        test: /\.ts$/,
        include: /src/,
        use: [{ loader: 'ts-loader' }]
      }
    ]
  },
  output: {
    path: path.resolve(__dirname, 'dist/main'),
    filename: 'main.js'
  },
  resolve: {
    extensions: ['.ts', '.js']
  }
};
