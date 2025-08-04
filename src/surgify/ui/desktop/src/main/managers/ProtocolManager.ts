import { protocol, net } from 'electron';
import log from 'electron-log';
import * as path from 'path';

export class ProtocolManager {
  public register(): void {
    // Register custom protocol for serving local files securely
    protocol.registerSchemesAsPrivileged([
      {
        scheme: 'surgify',
        privileges: {
          standard: true,
          secure: true,
          allowServiceWorkers: true,
          supportFetchAPI: true,
          corsEnabled: false
        }
      }
    ]);

    // Register protocol handler after app is ready
    protocol.registerFileProtocol('surgify', (request, callback) => {
      const url = request.url.substr(9); // Remove 'surgify://' prefix
      const filePath = path.join(__dirname, '../../renderer', url);
      
      log.info(`Protocol request for: ${url} -> ${filePath}`);
      callback({ path: filePath });
    });

    // Register HTTP/HTTPS protocols with custom handling
    protocol.registerHttpProtocol('surgify-secure', (request, callback) => {
      const url = request.url.replace('surgify-secure://', 'https://');
      
      // Validate the URL is from allowed domains
      if (this.isAllowedUrl(url)) {
        callback({ url });
      } else {
        log.warn(`Blocked request to unauthorized URL: ${url}`);
        callback({ error: -3 }); // ERR_ABORTED
      }
    });

    log.info('Custom protocols registered');
  }

  private isAllowedUrl(url: string): boolean {
    const allowedDomains = [
      'surgify.com',
      'api.surgify.com',
      'cdn.surgify.com',
      'assets.surgify.com'
    ];

    try {
      const parsedUrl = new URL(url);
      return allowedDomains.some(domain => 
        parsedUrl.hostname === domain || 
        parsedUrl.hostname.endsWith(`.${domain}`)
      );
    } catch {
      return false;
    }
  }

  public unregister(): void {
    try {
      protocol.unregisterProtocol('surgify');
      protocol.unregisterProtocol('surgify-secure');
      log.info('Custom protocols unregistered');
    } catch (error) {
      log.error('Failed to unregister protocols:', error);
    }
  }
}
