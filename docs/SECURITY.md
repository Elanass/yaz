# Security Guide

## Overview

This document outlines the security architecture, controls, and procedures for the YAZ Healthcare Platform. As a healthcare platform handling PHI (Protected Health Information), we implement comprehensive security measures to ensure HIPAA compliance and data protection.

## Security Architecture

### Defense in Depth

Our security model implements multiple layers of protection:

1. **Network Security**
   - TLS 1.3 encryption for all communications
   - Network segmentation and firewalls
   - VPN access for administrative functions

2. **Application Security**
   - OAuth 2.0 / OpenID Connect authentication
   - Role-based access control (RBAC)
   - Input validation and sanitization
   - SQL injection prevention

3. **Data Security**
   - Encryption at rest (AES-256)
   - Encryption in transit (TLS 1.3)
   - Database-level encryption for PHI
   - Secure key management

## Authentication and Authorization

### OAuth 2.0 / SMART on FHIR

```python
# Example OAuth configuration
OAUTH_CONFIG = {
    "authorization_endpoint": "https://auth.example.com/oauth2/authorize",
    "token_endpoint": "https://auth.example.com/oauth2/token",
    "scopes": [
        "patient/*.read",
        "user/*.read",
        "launch/patient"
    ]
}
```

### Role-Based Access Control

#### User Roles

1. **System Administrator**
   - Full system access
   - User management
   - System configuration

2. **Healthcare Provider**
   - Patient data access (assigned patients)
   - Clinical workflow functions
   - Documentation capabilities

3. **Clinical Staff**
   - Limited patient data access
   - Scheduling and coordination
   - Basic reporting

4. **Auditor**
   - Read-only access to audit logs
   - Compliance reporting
   - No PHI access

#### Permission Matrix

| Resource | Admin | Provider | Staff | Auditor |
|----------|-------|----------|-------|---------|
| Patient Data | RWD | RW* | R* | - |
| User Management | RWD | - | - | - |
| System Config | RW | - | - | - |
| Audit Logs | R | - | - | R |
| Reports | RWD | RW | R | R |

*Access limited to assigned patients only

### API Security

```python
# JWT token validation middleware
@app.middleware("http")
async def validate_jwt_token(request: Request, call_next):
    """Validate JWT tokens for API access."""
    token = request.headers.get("Authorization")
    if not token or not validate_token(token):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    return await call_next(request)
```

## Data Protection

### PHI Encryption

All PHI is encrypted using AES-256 encryption:

```python
# Example PHI encryption
from cryptography.fernet import Fernet

class PHIEncryption:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt_phi(self, data: str) -> str:
        """Encrypt PHI data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_phi(self, encrypted_data: str) -> str:
        """Decrypt PHI data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### Database Security

#### Connection Security

```python
# Secure database connection
DATABASE_CONFIG = {
    "url": "postgresql://user:pass@localhost:5432/yaz",
    "ssl_mode": "require",
    "ssl_cert": "/certs/client-cert.pem",
    "ssl_key": "/certs/client-key.pem",
    "ssl_ca": "/certs/ca-cert.pem"
}
```

#### Column-Level Encryption

```sql
-- Example encrypted PHI storage
CREATE TABLE patients (
    id UUID PRIMARY KEY,
    encrypted_ssn BYTEA,  -- AES-256 encrypted
    encrypted_dob BYTEA,  -- AES-256 encrypted
    name_hash VARCHAR(64), -- SHA-256 hash for indexing
    created_at TIMESTAMP DEFAULT NOW()
);
```

### File Storage Security

```python
# Secure file upload handling
@app.post("/upload")
async def upload_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user)
):
    """Securely handle file uploads."""
    
    # Validate file type
    if not validate_file_type(file.filename):
        raise HTTPException(400, "Invalid file type")
    
    # Scan for malware
    if not scan_file(file.file):
        raise HTTPException(400, "File failed security scan")
    
    # Encrypt and store
    encrypted_content = encrypt_file(file.file)
    return store_encrypted_file(encrypted_content, current_user.id)
```

## HIPAA Compliance

### Administrative Safeguards

1. **Security Officer**: Designated security officer responsible for HIPAA compliance
2. **Workforce Training**: Annual security awareness training
3. **Access Management**: Formal process for granting/revoking access
4. **Contingency Planning**: Business continuity and disaster recovery plans

### Physical Safeguards

1. **Facility Access**: Controlled access to data centers and offices
2. **Workstation Security**: Automatic screen locks, secure workstation policies
3. **Media Controls**: Secure disposal of electronic media containing PHI

### Technical Safeguards

1. **Access Control**: Unique user identification and authentication
2. **Audit Controls**: Comprehensive audit logging and monitoring
3. **Integrity**: PHI alteration/destruction protection
4. **Person/Entity Authentication**: Verify user identity before access
5. **Transmission Security**: End-to-end encryption for PHI transmission

## Audit Logging

### Audit Events

All security-relevant events are logged:

```python
# Example audit logging
class AuditLogger:
    def log_access(self, user_id: str, resource: str, action: str):
        """Log user access to resources."""
        audit_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent")
        }
        self.write_audit_log(audit_event)
```

### Audit Requirements

- **PHI Access**: Every access to PHI must be logged
- **Authentication**: All login attempts (successful and failed)
- **Authorization**: Access denials and privilege escalations
- **Data Modifications**: All create, update, delete operations
- **Administrative Actions**: User management, configuration changes

### Log Retention

- **Audit logs**: 6 years minimum (HIPAA requirement)
- **Application logs**: 1 year
- **Security logs**: 3 years
- **Backup logs**: 90 days

## Vulnerability Management

### Security Scanning

```yaml
# Automated security scanning
security_checks:
  - name: dependency_scan
    tool: safety
    schedule: daily
  
  - name: code_analysis
    tool: bandit
    schedule: on_commit
  
  - name: container_scan
    tool: trivy
    schedule: on_build
  
  - name: infrastructure_scan
    tool: nmap
    schedule: weekly
```

### Patch Management

1. **Critical vulnerabilities**: Patched within 24 hours
2. **High vulnerabilities**: Patched within 7 days
3. **Medium vulnerabilities**: Patched within 30 days
4. **Low vulnerabilities**: Patched within 90 days

### Penetration Testing

- **Annual**: Third-party penetration testing
- **Quarterly**: Internal vulnerability assessments
- **Continuous**: Automated security scanning

## Incident Response

### Security Incident Classification

#### Level 1 - Critical
- Data breach involving PHI
- Complete system compromise
- Active malware infection

#### Level 2 - High
- Unauthorized access to systems
- Denial of service attacks
- Significant security control failures

#### Level 3 - Medium
- Failed authentication attempts
- Minor security policy violations
- Non-critical vulnerability discoveries

#### Level 4 - Low
- Security awareness violations
- Low-risk vulnerability findings
- Policy clarification requests

### Response Procedures

#### Immediate Response (0-1 hour)
1. **Identify and contain** the incident
2. **Assess impact** and classification level
3. **Notify** incident response team
4. **Document** initial findings

#### Investigation (1-24 hours)
1. **Collect evidence** and preserve logs
2. **Analyze** attack vectors and impact
3. **Identify** root cause
4. **Develop** remediation plan

#### Recovery (24-72 hours)
1. **Implement** security fixes
2. **Restore** affected systems
3. **Verify** system integrity
4. **Monitor** for recurring issues

#### Post-Incident (72+ hours)
1. **Document** lessons learned
2. **Update** security procedures
3. **Conduct** post-mortem review
4. **Report** to stakeholders and regulators

## Breach Notification

### HIPAA Breach Notification Requirements

If a breach of PHI occurs:

1. **Individual Notification**: Within 60 days
2. **HHS Notification**: Within 60 days
3. **Media Notification**: If breach affects 500+ individuals
4. **Business Associate Notification**: Within 60 days

### Breach Assessment Criteria

A breach has occurred if:
- Unauthorized acquisition, access, use, or disclosure of PHI
- Compromises security or privacy of PHI
- Risk of harm to individuals

## Security Controls Checklist

### Technical Controls

- [ ] Multi-factor authentication enabled
- [ ] TLS 1.3 encryption for all communications
- [ ] Database encryption at rest configured
- [ ] API rate limiting implemented
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS protection headers
- [ ] CSRF protection enabled
- [ ] Secure session management
- [ ] Automated security scanning

### Administrative Controls

- [ ] Security policies documented
- [ ] Security awareness training completed
- [ ] Incident response plan tested
- [ ] Access control procedures implemented
- [ ] Regular security assessments scheduled
- [ ] Vendor risk assessments completed
- [ ] Business continuity plan documented
- [ ] Data retention policies enforced

### Physical Controls

- [ ] Facility access controls implemented
- [ ] Workstation security policies enforced
- [ ] Secure media disposal procedures
- [ ] Environmental monitoring systems
- [ ] Backup and recovery procedures tested

## Security Contacts

### Internal Contacts

- **Security Officer**: security-officer@organization.com
- **Privacy Officer**: privacy-officer@organization.com
- **Incident Response Team**: incident-response@organization.com
- **Compliance Team**: compliance@organization.com

### External Contacts

- **Legal Counsel**: legal@organization.com
- **Cyber Insurance**: insurance-provider@company.com
- **Law Enforcement**: Contact local FBI field office
- **HHS OCR**: https://www.hhs.gov/ocr/privacy/hipaa/complaints/

---

For additional security information, see:
- [Operations Guide](OPERATIONS.md)
- [Testing Guide](TESTING.md)
- [Architecture Overview](ARCHITECTURE.md)
