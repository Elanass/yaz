# Surgify Desktop Application Icons

This directory contains the application icons for different platforms:

- `icon.ico` - Windows icon
- `icon.icns` - macOS icon
- `icon.png` - Linux icon (512x512)

## Icon Requirements

### Windows (.ico)
- Multiple sizes: 16x16, 32x32, 48x48, 256x256
- Format: ICO

### macOS (.icns)
- Multiple sizes: 16x16, 32x32, 128x128, 256x256, 512x512
- Format: ICNS

### Linux (.png)
- Size: 512x512
- Format: PNG

## Generating Icons

You can use tools like:
- [electron-icon-builder](https://www.npmjs.com/package/electron-icon-builder)
- [icon-gen](https://www.npmjs.com/package/icon-gen)
- Online converters

Example using icon-gen:
```bash
npm install -g icon-gen
icon-gen -i icon-source.png -o ./assets --ico --icns
```
