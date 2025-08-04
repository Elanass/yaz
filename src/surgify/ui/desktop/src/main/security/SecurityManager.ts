import { Certificate } from 'electron';
import log from 'electron-log';
import Store from 'electron-store';

export interface SecurityConfig {
  trustedCertificates: string[];
  allowedDomains: string[];
  securityLevel: 'low' | 'medium' | 'high';
  enableCertificatePinning: boolean;
  blockExternalContent: boolean;
}

export class SecurityManager {
  private store: Store<SecurityConfig>;
  private trustedFingerprints: Set<string> = new Set();

  constructor() {
    this.store = new Store<SecurityConfig>({
      name: 'surgify-security',
      defaults: {
        trustedCertificates: [],
        allowedDomains: ['surgify.com', 'api.surgify.com', 'localhost'],
        securityLevel: 'high',
        enableCertificatePinning: true,
        blockExternalContent: true
      }
    });

    this.loadTrustedCertificates();
  }

  private loadTrustedCertificates(): void {
    const certificates = this.store.get('trustedCertificates', []);
    this.trustedFingerprints = new Set(certificates);
    log.info(`Loaded ${certificates.length} trusted certificates`);
  }

  public isTrustedCertificate(certificate: Certificate): boolean {
    if (!this.store.get('enableCertificatePinning', true)) {
      return true; // Certificate pinning disabled
    }

    const fingerprint = this.getCertificateFingerprint(certificate);
    const isTrusted = this.trustedFingerprints.has(fingerprint);
    
    if (!isTrusted) {
      log.warn(`Untrusted certificate detected: ${fingerprint}`);
    }

    return isTrusted;
  }

  public addTrustedCertificate(certificate: Certificate): void {
    const fingerprint = this.getCertificateFingerprint(certificate);
    this.trustedFingerprints.add(fingerprint);
    
    const certificates = Array.from(this.trustedFingerprints);
    this.store.set('trustedCertificates', certificates);
    
    log.info(`Added trusted certificate: ${fingerprint}`);
  }

  public removeTrustedCertificate(certificate: Certificate): void {
    const fingerprint = this.getCertificateFingerprint(certificate);
    this.trustedFingerprints.delete(fingerprint);
    
    const certificates = Array.from(this.trustedFingerprints);
    this.store.set('trustedCertificates', certificates);
    
    log.info(`Removed trusted certificate: ${fingerprint}`);
  }

  public isAllowedDomain(domain: string): boolean {
    const allowedDomains = this.store.get('allowedDomains', []);
    return allowedDomains.some(allowed => 
      domain === allowed || domain.endsWith(`.${allowed}`)
    );
  }

  public addAllowedDomain(domain: string): void {
    const allowedDomains = this.store.get('allowedDomains', []);
    if (!allowedDomains.includes(domain)) {
      allowedDomains.push(domain);
      this.store.set('allowedDomains', allowedDomains);
      log.info(`Added allowed domain: ${domain}`);
    }
  }

  public removeAllowedDomain(domain: string): void {
    const allowedDomains = this.store.get('allowedDomains', []);
    const index = allowedDomains.indexOf(domain);
    if (index > -1) {
      allowedDomains.splice(index, 1);
      this.store.set('allowedDomains', allowedDomains);
      log.info(`Removed allowed domain: ${domain}`);
    }
  }

  public getSecurityLevel(): 'low' | 'medium' | 'high' {
    return this.store.get('securityLevel', 'high');
  }

  public setSecurityLevel(level: 'low' | 'medium' | 'high'): void {
    this.store.set('securityLevel', level);
    log.info(`Security level changed to: ${level}`);
  }

  public shouldBlockExternalContent(): boolean {
    return this.store.get('blockExternalContent', true);
  }

  public validateUrl(url: string): boolean {
    try {
      const parsedUrl = new URL(url);
      
      // Check protocol
      if (!['https:', 'http:'].includes(parsedUrl.protocol)) {
        log.warn(`Invalid protocol: ${parsedUrl.protocol}`);
        return false;
      }

      // Check domain
      if (!this.isAllowedDomain(parsedUrl.hostname)) {
        log.warn(`Disallowed domain: ${parsedUrl.hostname}`);
        return false;
      }

      // Additional security checks based on security level
      const securityLevel = this.getSecurityLevel();
      
      if (securityLevel === 'high') {
        // High security: Only HTTPS for production domains
        if (parsedUrl.protocol === 'http:' && !parsedUrl.hostname.includes('localhost')) {
          log.warn(`HTTP not allowed in high security mode: ${url}`);
          return false;
        }
      }

      return true;
    } catch (error) {
      log.error(`URL validation error: ${error}`);
      return false;
    }
  }

  public getContentSecurityPolicy(): string {
    const securityLevel = this.getSecurityLevel();
    const allowedDomains = this.store.get('allowedDomains', []);
    
    const domainList = allowedDomains.map(domain => `https://${domain}`).join(' ');
    
    switch (securityLevel) {
      case 'high':
        return `default-src 'self' ${domainList}; ` +
               `script-src 'self' ${domainList}; ` +
               `style-src 'self' 'unsafe-inline' ${domainList}; ` +
               `img-src 'self' data: ${domainList}; ` +
               `connect-src 'self' ${domainList}; ` +
               `frame-src 'none'; ` +
               `object-src 'none'; ` +
               `media-src 'self' ${domainList};`;
      
      case 'medium':
        return `default-src 'self' ${domainList}; ` +
               `script-src 'self' 'unsafe-inline' ${domainList}; ` +
               `style-src 'self' 'unsafe-inline' ${domainList}; ` +
               `img-src 'self' data: ${domainList}; ` +
               `connect-src 'self' ${domainList};`;
      
      case 'low':
        return `default-src 'self' 'unsafe-inline' 'unsafe-eval' ${domainList}; ` +
               `connect-src 'self' ${domainList};`;
      
      default:
        return this.getContentSecurityPolicy(); // Default to high
    }
  }

  private getCertificateFingerprint(certificate: Certificate): string {
    // In a real implementation, you would compute the SHA-256 fingerprint
    // For now, we'll use the subject as a simple identifier
    return certificate.subject || 'unknown';
  }

  public exportSettings(): SecurityConfig {
    return {
      trustedCertificates: Array.from(this.trustedFingerprints),
      allowedDomains: this.store.get('allowedDomains', []),
      securityLevel: this.store.get('securityLevel', 'high'),
      enableCertificatePinning: this.store.get('enableCertificatePinning', true),
      blockExternalContent: this.store.get('blockExternalContent', true)
    };
  }

  public importSettings(config: Partial<SecurityConfig>): void {
    if (config.trustedCertificates) {
      this.trustedFingerprints = new Set(config.trustedCertificates);
      this.store.set('trustedCertificates', config.trustedCertificates);
    }
    
    if (config.allowedDomains) {
      this.store.set('allowedDomains', config.allowedDomains);
    }
    
    if (config.securityLevel) {
      this.store.set('securityLevel', config.securityLevel);
    }
    
    if (config.enableCertificatePinning !== undefined) {
      this.store.set('enableCertificatePinning', config.enableCertificatePinning);
    }
    
    if (config.blockExternalContent !== undefined) {
      this.store.set('blockExternalContent', config.blockExternalContent);
    }
    
    log.info('Security settings imported');
  }
}
