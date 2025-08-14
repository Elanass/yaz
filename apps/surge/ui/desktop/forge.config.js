const path = require('path');

module.exports = {
  packagerConfig: {
    name: 'Surgify',
    executableName: 'surgify',
    icon: path.resolve(__dirname, 'assets', 'icon'),
    extraResource: [
      path.resolve(__dirname, 'assets')
    ]
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {
        name: 'surgify'
      }
    },
    {
      name: '@electron-forge/maker-zip',
      platforms: ['darwin']
    },
    {
      name: '@electron-forge/maker-deb',
      config: {
        options: {
          maintainer: 'Surgify Team',
          homepage: 'https://surgify.com'
        }
      }
    },
    {
      name: '@electron-forge/maker-rpm',
      config: {
        options: {
          maintainer: 'Surgify Team',
          homepage: 'https://surgify.com'
        }
      }
    }
  ],
  plugins: [
    {
      name: '@electron-forge/plugin-webpack',
      config: {
        mainConfig: './webpack.main.config.js',
        renderer: {
          config: './webpack.renderer.config.js',
          entryPoints: [
            {
              html: './src/renderer/index.html',
              js: './src/renderer/renderer.ts',
              name: 'main_window'
            }
          ]
        }
      }
    }
  ]
};
