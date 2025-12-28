# Cisco FMC 7.6.2 REST API Automation

This project provides examples and best practices for automating Cisco Firepower Management Center (FMC) 7.6.2 using its REST API.

## Prerequisites

- Cisco FMC version 7.6.2
- Python 3.8 or higher
- Network access to FMC (HTTPS/443)
- Valid FMC user account with appropriate privileges

## FMC Configuration Requirements

### 1. Enable REST API Access

The REST API is enabled by default in FMC 7.6.2, but you need to configure proper access:

1. **Create API User Account**:
   - Navigate to **System > Users > Users**
   - Click **Add User**
   - Create a dedicated user for API access (e.g., `api_automation`)
   - Assign appropriate role (Security Analyst, Network Admin, or custom role)
   - Set a strong password complying with password policy

2. **Configure User Role Permissions**:
   - Navigate to **System > Users > User Roles**
   - For API automation, minimum required permissions:
     - **Policy Configuration**: Read/Write (for policy automation)
     - **Object Manager**: Read/Write (for network objects, etc.)
     - **Device Management**: Read/Write (for device operations)
     - **System Configuration**: Read (for retrieving system info)
   - Create custom role if needed for least privilege

3. **Enable External Authentication (Optional but Recommended)**:
   - Navigate to **System > Integration > LDAP**
   - Configure LDAP/RADIUS for centralized authentication
   - Benefits: Better audit trails, centralized credential management

4. **Configure IP Whitelist (Highly Recommended)**:
   - Navigate to **System > Configuration > REST API Preferences**
   - Enable IP-based access control
   - Add only trusted source IPs/networks
   - This restricts API access to known automation servers

5. **Enable Audit Logging**:
   - Navigate to **System > Integration > Syslog Alerts**
   - Configure syslog server to capture all API activities
   - Monitor for unauthorized access attempts

6. **TLS/SSL Configuration**:
   - Navigate to **System > Configuration > HTTPS Certificate**
   - Install valid SSL certificate (avoid self-signed in production)
   - Enforce TLS 1.2 or higher

### 2. Network Requirements

- Ensure firewall rules allow HTTPS (TCP/443) from automation host to FMC
- Use dedicated management network for API access
- Consider VPN if accessing from external networks

### 3. Rate Limiting Awareness

- FMC has built-in rate limiting (default: 120 requests/minute)
- Implement exponential backoff in your scripts
- Use bulk operations where possible

## Security Best Practices

1. **Credential Management**:
   - Never hardcode credentials in scripts
   - Use environment variables or secure vaults (HashiCorp Vault, AWS Secrets Manager)
   - Rotate API credentials regularly (90 days recommended)

2. **API User Principle of Least Privilege**:
   - Create role-based users for specific automation tasks
   - Avoid using admin accounts for routine automation

3. **Token Management**:
   - FMC tokens expire after 30 minutes
   - Implement token refresh logic
   - Properly handle token expiration errors

4. **Secure Communication**:
   - Always use HTTPS
   - Verify SSL certificates (disable only in lab/testing)
   - Use certificate pinning for critical applications

5. **Audit and Monitoring**:
   - Log all API calls with timestamps
   - Monitor for unusual patterns (failed authentications, excessive requests)
   - Set up alerts for security events

6. **Version Control**:
   - Store automation scripts in Git with .gitignore for secrets
   - Use code review for changes
   - Tag releases for rollback capability

## Project Structure

```
.
├── README.md                    # This file
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
├── config/
│   └── fmc_config.py         # Configuration management
├── lib/
│   ├── fmc_client.py         # Core FMC API client
│   └── utils.py              # Helper functions
└── examples/
    ├── 01_authentication.py   # Authentication examples
    ├── 02_network_objects.py  # Network object management
    ├── 03_access_policies.py  # Access policy automation
    ├── 04_nat_policies.py     # NAT policy management
    ├── 05_device_management.py # Device operations
    └── 06_bulk_operations.py  # Bulk automation examples
```

## Quick Start

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure your FMC credentials
4. Run examples starting with authentication

## API Documentation

Official Cisco FMC REST API documentation:
- FMC REST API Guide: https://www.cisco.com/c/en/us/td/docs/security/firepower/api/REST/
- Interactive API Explorer: `https://your-fmc-ip/api/api-explorer/`

## Support

For issues and questions, refer to Cisco TAC or community forums.
