# Cisco FMC 7.6.2 REST API Automation - Complete Guide

## Quick Summary

This project provides a complete, production-ready framework for automating Cisco Firepower Management Center (FMC) 7.6.2 using Python and its REST API.

## What's Included

### 📁 Core Library (`lib/`)
- **fmc_client.py**: Full-featured FMC API client with authentication, token management, retry logic
- **utils.py**: Helper functions for validation, rate limiting, error formatting

### ⚙️ Configuration (`config/`)
- **fmc_config.py**: Centralized configuration management from environment variables

### 📚 Examples (`examples/`)
1. **00_quick_start.py** - Start here! Complete end-to-end example
2. **01_authentication.py** - Auth patterns, token management, context managers
3. **02_network_objects.py** - Create/read/update/delete network objects
4. **03_access_policies.py** - Policy and access rule management
5. **05_device_management.py** - Device operations and deployments
6. **06_bulk_operations.py** - Bulk automation, CSV import/export

### 📖 Documentation
- **README.md** - Main documentation with FMC setup steps
- **SECURITY_BEST_PRACTICES.md** - Comprehensive security guide
- **.env.example** - Configuration template

## FMC Configuration Steps (Required)

### 1. Create API User Account
```
FMC UI: System > Users > Users > Add User

Settings:
- Username: api_automation (or your preference)
- Password: Strong 20+ character password
- User Role: Custom role with minimal required permissions
```

### 2. Configure API User Role
```
FMC UI: System > Users > User Roles

Minimum Permissions:
✓ Policy Configuration: Read/Write (if managing policies)
✓ Object Manager: Read/Write (if managing objects)
✓ Device Management: Read (Write if deploying)
✓ System Configuration: Read only
✗ User Management: None
```

### 3. Enable IP Whitelist (Highly Recommended)
```
FMC UI: System > Configuration > REST API Preferences

- Enable "Host Allowlist"
- Add IP addresses of automation servers
- Use /32 for single hosts
```

### 4. Configure Audit Logging
```
FMC UI: System > Integration > Syslog Alerts

- Configure external syslog server
- Enable logging for all API activities
- Monitor for security events
```

### 5. Install Valid SSL Certificate (Production)
```
FMC UI: System > Configuration > HTTPS Certificate

- Generate CSR
- Submit to Certificate Authority
- Install signed certificate
- Enforce TLS 1.2+
```

## Installation & Setup

### 1. Install Python Dependencies
```bash
cd "/Users/ngubanov/Documents/Projects/CL/Vibe Coding"
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
nano .env  # Edit with your FMC details
```

**Required in .env:**
```bash
FMC_HOST=your-fmc-ip-or-hostname
FMC_USERNAME=api_automation
FMC_PASSWORD=YourSecurePassword123!
FMC_VERIFY_SSL=true  # false only for lab
```

### 3. Test Connection
```bash
python examples/00_quick_start.py
```

Expected output:
```
✓ Connected and authenticated successfully
✓ FMC Version: 7.6.2
...
Quick Start Completed Successfully!
```

## Key Features

### 🔐 Security
- ✅ No hardcoded credentials
- ✅ Environment variable management
- ✅ Automatic token refresh
- ✅ Token cleanup on exit
- ✅ SSL/TLS verification
- ✅ Rate limiting with exponential backoff
- ✅ Input validation
- ✅ Comprehensive error handling

### 🚀 Reliability
- ✅ Automatic retry with exponential backoff
- ✅ Connection pooling
- ✅ Token expiration handling
- ✅ Graceful error recovery
- ✅ Pagination support for large datasets
- ✅ Context managers for cleanup

### 📊 Functionality
- ✅ Authentication & session management
- ✅ Network object management (hosts, networks, ranges)
- ✅ Access policy automation
- ✅ Access rule management
- ✅ Device operations
- ✅ Configuration deployment
- ✅ Bulk operations
- ✅ CSV import/export

## Usage Examples

### Basic Authentication
```python
from lib.fmc_client import FMCClient

# Context manager automatically handles login/logout
with FMCClient() as client:
    # Get system info
    info = client.get("info/serverversion")
    print(f"FMC Version: {info['items'][0]['serverVersion']}")
```

### Create Network Object
```python
from lib.fmc_client import FMCClient

with FMCClient() as client:
    data = {
        "name": "Web_Server",
        "type": "Host",
        "value": "10.1.1.10",
        "description": "Production web server"
    }
    result = client.post("object/hosts", data)
    print(f"Created: {result['name']}")
```

### Bulk Operations
```python
from lib.fmc_client import FMCClient

servers = [
    ("Server_01", "10.1.1.1", "App server 1"),
    ("Server_02", "10.1.1.2", "App server 2"),
    # ... more servers
]

with FMCClient() as client:
    for name, ip, desc in servers:
        data = {
            "name": name,
            "type": "Host",
            "value": ip,
            "description": desc
        }
        result = client.post("object/hosts", data)
        print(f"✓ Created: {name}")
```

### Deploy to Device
```python
from lib.fmc_client import FMCClient
import time

with FMCClient() as client:
    # Deploy changes
    deployment = client.post("deployment/deploymentrequests", {
        "type": "DeploymentRequest",
        "version": int(time.time()),
        "deviceList": ["device-uuid-here"]
    })
    
    # Check status
    status = client.get(f"deployment/deploymentrequests/{deployment['id']}")
    print(f"Status: {status['deploymentState']}")
```

## Best Practices

### 1. Always Use Context Managers
```python
# ✓ CORRECT - Automatic cleanup
with FMCClient() as client:
    client.get("object/hosts")

# ❌ WRONG - Manual cleanup required
client = FMCClient()
client.authenticate()
client.get("object/hosts")
client.logout()  # Easy to forget!
```

### 2. Validate Input
```python
from lib.utils import validate_ip_address, validate_ip_network

ip = user_input_ip
if not validate_ip_address(ip):
    raise ValueError(f"Invalid IP: {ip}")
```

### 3. Handle Errors Gracefully
```python
result = client.post("object/hosts", data)
if result:
    print(f"✓ Success: {result['name']}")
else:
    print(f"✗ Failed - check logs")
```

### 4. Use Bulk Operations for Scale
```python
from lib.utils import chunk_list

# Split large operations into chunks
for chunk in chunk_list(large_list, 50):
    process_chunk(chunk)
```

### 5. Never Commit Secrets
```bash
# Always in .gitignore
.env
*.pem
credentials/
```

## API Rate Limits

- **Default**: 120 requests/minute
- **Token Lifetime**: 30 minutes
- **Automatic Retry**: Built into client (exponential backoff)

The client automatically:
- Rates limits to 100 req/min (configurable)
- Refreshes tokens before expiry
- Retries on transient failures

## Common Use Cases

### 1. Daily Network Object Sync
```python
# Sync network objects from CMDB to FMC
cmdb_data = fetch_from_cmdb()
for record in cmdb_data:
    create_or_update_object(record)
```

### 2. Policy Compliance Checks
```python
# Verify policies meet compliance requirements
policies = client.get_all_pages("policy/accesspolicies")
for policy in policies:
    verify_compliance(policy)
```

### 3. Automated Deployments
```python
# Deploy during maintenance window
if in_maintenance_window():
    deploy_pending_changes()
    verify_deployment_success()
```

### 4. Configuration Backups
```python
# Export configurations for backup
objects = export_all_objects()
save_to_backup(objects, timestamp)
```

## Troubleshooting

### Connection Issues
```
Error: Connection refused
→ Check FMC is accessible: ping <fmc-ip>
→ Verify HTTPS port 443 is open
→ Check firewall rules
```

### Authentication Failures
```
Error: Authentication failed (401)
→ Verify credentials in .env
→ Check user account is not locked
→ Confirm user has API permissions
→ Check IP whitelist if enabled
```

### SSL Certificate Errors
```
Error: SSL certificate verify failed
→ Production: Install valid certificate on FMC
→ Lab: Set FMC_VERIFY_SSL=false in .env (not for production!)
→ Or: Set FMC_CA_CERT=/path/to/ca-bundle.crt
```

### Rate Limiting
```
Error: 429 Too Many Requests
→ Built-in rate limiting should prevent this
→ If occurs, increase wait time in utils.py
→ Check for concurrent scripts
```

## Security Checklist

Before deploying to production:

- [ ] Credentials in environment variables or vault (not hardcoded)
- [ ] SSL certificate verification enabled
- [ ] Valid SSL certificate installed on FMC
- [ ] API user with minimal required permissions
- [ ] IP whitelist configured on FMC
- [ ] Audit logging enabled and monitored
- [ ] .gitignore configured properly
- [ ] Regular password rotation schedule
- [ ] Code reviewed by security team
- [ ] Tested in lab environment first

See **SECURITY_BEST_PRACTICES.md** for complete security guide.

## API Documentation

- **FMC API Explorer**: `https://your-fmc-ip/api/api-explorer/`
- **Cisco API Documentation**: https://www.cisco.com/c/en/us/td/docs/security/firepower/api/REST/
- **API Version**: v1 (FMC 7.6.2)

## Project Structure
```
.
├── README.md                       # Main documentation + FMC setup
├── SECURITY_BEST_PRACTICES.md     # Security guide
├── requirements.txt                # Python dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git exclusions
├── config/
│   └── fmc_config.py             # Configuration management
├── lib/
│   ├── fmc_client.py             # Core API client
│   └── utils.py                  # Helper functions
└── examples/
    ├── 00_quick_start.py         # START HERE
    ├── 01_authentication.py      # Auth patterns
    ├── 02_network_objects.py     # Object management
    ├── 03_access_policies.py     # Policy automation
    ├── 05_device_management.py   # Device operations
    └── 06_bulk_operations.py     # Bulk automation
```

## Next Steps

1. **Complete FMC Configuration** (see above)
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Configure .env File**: Copy from .env.example
4. **Run Quick Start**: `python examples/00_quick_start.py`
5. **Explore Examples**: Review and run example scripts
6. **Read Security Guide**: SECURITY_BEST_PRACTICES.md
7. **Build Your Automation**: Use examples as templates

## Support & Resources

- **FMC API Explorer**: Interactive API documentation on your FMC
- **Cisco TAC**: Technical support for FMC issues
- **Project Issues**: Review code comments and documentation

## License & Disclaimer

This is example code for educational and automation purposes. Always:
- Test thoroughly in lab before production
- Follow your organization's change management
- Adhere to security policies
- Maintain proper backups

---

**Version**: 1.0  
**Compatible with**: Cisco FMC 7.6.2  
**Python**: 3.8+  
**Last Updated**: December 2025

Happy Automating! 🚀
