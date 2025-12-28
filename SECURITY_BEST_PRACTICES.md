# Cisco FMC REST API - Security Best Practices

## Overview
This document outlines security best practices for automating Cisco FMC 7.6.2 using its REST API.

## 1. FMC Configuration Security

### 1.1 User Account Management

**Create Dedicated API Users:**
```
System > Users > Users > Add User
- Username: api_automation (descriptive, not generic)
- Authentication: Local or LDAP
- User Role: Custom role with minimal required permissions
- Password: Strong, unique password (20+ characters recommended)
```

**Password Requirements:**
- Minimum 20 characters
- Mix of uppercase, lowercase, numbers, special characters
- No dictionary words
- Not reused from other systems
- Rotated every 90 days

**Custom Role Creation:**
```
System > Users > User Roles > Add User Role
Required Permissions (Principle of Least Privilege):
✓ Policy Configuration: Read/Write (if managing policies)
✓ Object Manager: Read/Write (if managing objects)
✓ Device Management: Read only (unless deploying)
✗ System Configuration: Read only (not Write)
✗ User Management: None (API should not manage users)
```

### 1.2 IP Whitelisting

**Configure in FMC:**
```
System > Configuration > REST API Preferences
- Enable "Host Allowlist"
- Add only automation server IPs
- Use /32 for single hosts
- Document each entry with purpose
```

**Example Configuration:**
```
10.1.100.50/32    - Primary automation server
10.1.100.51/32    - Backup automation server
192.168.1.100/32  - DevOps workstation (temporary, review quarterly)
```

### 1.3 Certificate Management

**Replace Self-Signed Certificates:**
```
System > Configuration > HTTPS Certificate
1. Generate CSR in FMC
2. Submit to corporate/public CA
3. Install signed certificate
4. Force TLS 1.2+ only
```

**Certificate Validation in Scripts:**
```python
# Production - Always verify certificates
FMC_VERIFY_SSL=true
FMC_CA_CERT=/path/to/ca-bundle.crt

# Lab/Testing only - Can disable with warning
FMC_VERIFY_SSL=false  # NOT for production!
```

### 1.4 Audit Logging

**Enable Comprehensive Logging:**
```
System > Integration > Syslog Alerts
- Send to centralized syslog server
- Log all API authentication events
- Log all configuration changes
- Retain logs for compliance period (typically 1 year+)
```

**Monitor for:**
- Failed authentication attempts (>3 in 5 minutes = alert)
- API calls from unexpected IPs
- Bulk operations outside maintenance windows
- Unauthorized access attempts

## 2. Credential Management

### 2.1 Never Hardcode Credentials

**❌ WRONG:**
```python
username = "admin"
password = "Password123!"
```

**✓ CORRECT:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('FMC_USERNAME')
password = os.getenv('FMC_PASSWORD')
```

### 2.2 Use Secret Management Solutions

**Recommended Options:**

**HashiCorp Vault:**
```python
import hvac

client = hvac.Client(url='https://vault.example.com')
secret = client.secrets.kv.v2.read_secret_version(path='fmc/credentials')
username = secret['data']['data']['username']
password = secret['data']['data']['password']
```

**AWS Secrets Manager:**
```python
import boto3

client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='prod/fmc/credentials')
credentials = json.loads(response['SecretString'])
```

**Azure Key Vault:**
```python
from azure.keyvault.secrets import SecretClient

client = SecretClient(vault_url="https://myvault.vault.azure.net", credential=credential)
secret = client.get_secret("fmc-password")
```

### 2.3 Environment-Specific Credentials

```bash
# Development
.env.dev

# Staging
.env.staging

# Production
.env.prod  # Never commit to Git!
```

### 2.4 Credential Rotation

**Automated Rotation Script:**
```python
def rotate_fmc_password():
    """Rotate FMC API user password every 90 days."""
    # 1. Generate new strong password
    new_password = generate_secure_password(length=24)
    
    # 2. Update in FMC (use admin account)
    update_user_password(api_username, new_password)
    
    # 3. Update in secret vault
    update_vault_secret('fmc/credentials', password=new_password)
    
    # 4. Test new credentials
    test_api_connection()
    
    # 5. Log rotation event
    log_security_event("API password rotated")
```

## 3. API Security

### 3.1 Token Management

**Security Measures:**
```python
class FMCClient:
    def __init__(self):
        self.token = None
        self.token_expiry = 0
        
    def authenticate(self):
        # Get token (30-minute lifetime)
        # Store in memory only, never disk
        
    def logout(self):
        # Always revoke token when done
        self.revoke_token()
        self.token = None  # Clear from memory
        
    def __del__(self):
        # Ensure cleanup on object destruction
        if self.token:
            self.logout()
```

**Never:**
- Store tokens in files
- Log tokens
- Pass tokens in URLs
- Share tokens between processes

### 3.2 Rate Limiting

**Implement Client-Side Rate Limiting:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30)
)
def api_call_with_retry():
    # Automatic retry with exponential backoff
    pass
```

**Respect FMC Limits:**
- Default: 120 requests/minute
- Monitor 429 (Too Many Requests) responses
- Implement backoff on rate limit errors

### 3.3 Input Validation

**Always Validate User Input:**
```python
def validate_ip_address(ip: str) -> bool:
    """Validate IPv4 address format."""
    import re
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)

def sanitize_object_name(name: str) -> str:
    """Remove potentially dangerous characters."""
    # Allow only alphanumeric, underscore, hyphen
    import re
    return re.sub(r'[^a-zA-Z0-9_-]', '', name)
```

### 3.4 Error Handling

**Don't Leak Sensitive Information:**
```python
# ❌ WRONG - Exposes internal details
try:
    client.authenticate()
except Exception as e:
    print(f"Error: {e}")  # Might include credentials or internal IPs

# ✓ CORRECT - Generic error message
try:
    client.authenticate()
except Exception as e:
    logger.error("Authentication failed", exc_info=True)
    print("Authentication failed. Check logs for details.")
```

## 4. Network Security

### 4.1 Secure Communication

**TLS Configuration:**
```python
import ssl
import requests

# Create secure SSL context
context = ssl.create_default_context()
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.maximum_version = ssl.TLSVersion.TLSv1_3

# Use with requests
session = requests.Session()
session.verify = '/path/to/ca-bundle.crt'
```

### 4.2 Network Segmentation

**Recommended Architecture:**
```
[Automation Server] ---> [Management Network] ---> [FMC]
     10.1.100.50            10.1.0.0/24           10.1.10.10

Firewall Rules:
- Allow: 10.1.100.50 -> 10.1.10.10:443 (HTTPS)
- Deny: All other traffic to FMC
```

### 4.3 Use VPN for Remote Access

```
Remote Automation --> VPN Gateway --> Management Network --> FMC
```

## 5. Code Security

### 5.1 Git Security

**.gitignore:**
```gitignore
# Never commit these
.env
.env.*
*.pem
*.key
credentials/
secrets/
*.log
```

**Pre-commit Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for potential secrets
if git diff --cached | grep -E '(password|secret|api[_-]?key|token).*=.*["\']'; then
    echo "❌ Potential credential found in commit!"
    echo "Remove sensitive data before committing."
    exit 1
fi
```

### 5.2 Dependency Security

**Scan for Vulnerabilities:**
```bash
# Regular security scans
pip install safety
safety check

# Or use
pip-audit
```

**Keep Dependencies Updated:**
```bash
pip list --outdated
pip install --upgrade <package>
```

### 5.3 Code Review

**Required Reviews:**
- All API integration code
- Authentication/authorization logic
- Credential handling
- Production deployment scripts

## 6. Operational Security

### 6.1 Principle of Least Privilege

**Access Levels:**
```
Read-only Automation:
- View configurations
- Generate reports
- No modifications

Configuration Automation:
- Create/modify objects
- Update policies
- No deployments (requires approval)

Full Automation:
- All configuration changes
- Policy deployments
- Requires additional approval
```

### 6.2 Change Management

**Automation Change Process:**
1. Submit change request
2. Peer review code
3. Test in lab environment
4. Get approval
5. Schedule maintenance window
6. Execute with rollback plan
7. Verify and document

### 6.3 Monitoring and Alerting

**Set Up Alerts:**
```python
# Alert on suspicious activity
def check_security_events():
    events = fmc.get_audit_logs(since=last_check)
    
    for event in events:
        if event['type'] == 'failed_auth' and event['count'] > 3:
            send_alert("Multiple failed auth attempts from " + event['ip'])
        
        if event['type'] == 'bulk_delete' and not in_maintenance_window():
            send_alert("Unexpected bulk deletion outside maintenance window")
```

## 7. Compliance and Documentation

### 7.1 Document Everything

**Required Documentation:**
- API user accounts and purposes
- Automation workflows
- Security exceptions and justifications
- Incident response procedures
- Credential rotation schedule

### 7.2 Regular Security Reviews

**Quarterly Review Checklist:**
- [ ] Review API user permissions
- [ ] Audit IP whitelist (remove unused entries)
- [ ] Check for outdated credentials
- [ ] Review audit logs for anomalies
- [ ] Update dependency versions
- [ ] Test disaster recovery procedures
- [ ] Review and update documentation

### 7.3 Compliance Requirements

**Common Standards:**
- **PCI DSS**: Secure credential storage, audit logging
- **HIPAA**: Access controls, encryption in transit
- **SOC 2**: Change management, monitoring
- **GDPR**: Data protection, access logging

## 8. Incident Response

### 8.1 Credential Compromise

**Response Plan:**
1. **Immediately** revoke compromised credentials
2. Create new credentials with different username
3. Review audit logs for unauthorized access
4. Check for unauthorized configuration changes
5. Restore from backup if needed
6. Update all automation scripts
7. Document incident
8. Review and improve security controls

### 8.2 Unauthorized API Access

**Response Steps:**
1. Block source IP at firewall
2. Revoke all API tokens
3. Enable additional authentication (if available)
4. Review and restrict IP whitelist
5. Investigate source of compromise
6. Implement additional monitoring

## Summary Checklist

### FMC Configuration
- [ ] Dedicated API user with minimal permissions
- [ ] Strong password (20+ characters)
- [ ] IP whitelist enabled and restrictive
- [ ] Valid SSL certificate installed
- [ ] TLS 1.2+ enforced
- [ ] Audit logging to external syslog
- [ ] Regular password rotation (90 days)

### Script Security
- [ ] Credentials in environment variables or vault
- [ ] No hardcoded secrets
- [ ] SSL verification enabled (except lab)
- [ ] Rate limiting implemented
- [ ] Input validation on all user input
- [ ] Proper error handling (no info leakage)
- [ ] Automatic token cleanup/revocation

### Operational Security
- [ ] Version control with .gitignore for secrets
- [ ] Code review process
- [ ] Regular dependency updates
- [ ] Vulnerability scanning
- [ ] Change management process
- [ ] Incident response plan
- [ ] Regular security audits

### Monitoring
- [ ] Centralized logging
- [ ] Failed authentication alerts
- [ ] Unusual activity detection
- [ ] Performance monitoring
- [ ] Regular log reviews

## Additional Resources

- **Cisco FMC Security Guide**: https://www.cisco.com/c/en/us/support/security/defense-center/products-installation-and-configuration-guides-list.html
- **OWASP API Security**: https://owasp.org/www-project-api-security/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **CIS Controls**: https://www.cisecurity.org/controls/

---

**Remember**: Security is not a one-time task but an ongoing process. Regularly review and update your security practices as threats evolve.
