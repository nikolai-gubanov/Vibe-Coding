# Update Policy Logging Script

## Purpose
This script updates the "Vibe Coding Demo Policy" access control policy to configure logging options based on rule actions.

## What It Does

For each rule in the policy:
- **ALLOW rules**: Adds "Log at end of connection" option
- **BLOCK rules**: Adds "Log at beginning of connection" option
- **All rules**: Enables "Send Connection Events to FMC"

## Prerequisites

1. **Configure .env file** with your FMC credentials:
   ```bash
   FMC_HOST=your-fmc-ip-or-hostname
   FMC_USERNAME=your-api-username
   FMC_PASSWORD=your-password
   FMC_VERIFY_SSL=true  # or false for lab
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **FMC must have**:
   - A policy named "Vibe Coding Demo Policy"
   - API access configured (see main README.md)

## Usage

```bash
python update_policy_logging.py
```

## Example Output

```
============================================================
Update Access Control Policy - Logging Configuration
============================================================

[Step 1] Finding policy: Vibe Coding Demo Policy
✓ Found policy: Vibe Coding Demo Policy
  Policy ID: 12345-abcde-67890

[Step 2] Retrieving all rules in policy...
✓ Found 5 rules

[Step 3] Updating logging configuration for each rule...

  [1/5] Allow Web Traffic
    Action: ALLOW
    Logging: End of connection ✓
    ✓ Updated successfully

  [2/5] Block Malicious Sites
    Action: BLOCK
    Logging: Beginning of connection ✓
    ✓ Updated successfully

============================================================
Update Summary:
  Total rules: 5
  ✓ Updated: 5
  ⊘ Skipped: 0
  ✗ Failed: 0
============================================================

⚠ IMPORTANT: Changes have been made to the policy.
   You need to deploy to devices for changes to take effect.
```

## After Running

1. **Review changes** in FMC UI:
   - Go to Policies > Access Control
   - Open "Vibe Coding Demo Policy"
   - Verify logging settings on each rule

2. **Deploy to devices**:
   - Navigate to Deploy > Deployment
   - Select devices
   - Click Deploy
   
   Or use the device management script:
   ```bash
   python examples/05_device_management.py
   ```

3. **Verify logging**:
   - Check Analysis > Connection Events
   - Verify events are being logged

## Logging Configuration Details

| Rule Action | Log Begin | Log End | Send to FMC |
|-------------|-----------|---------|-------------|
| ALLOW       | ✗         | ✓       | ✓           |
| BLOCK       | ✓         | ✗       | ✓           |
| Other       | (unchanged) | (unchanged) | ✓     |

## Troubleshooting

**Policy not found:**
- Verify the policy name is exactly "Vibe Coding Demo Policy"
- Check the policy exists in FMC UI
- Script will list all available policies if not found

**Authentication failed:**
- Verify credentials in .env file
- Check user has appropriate permissions
- Ensure API access is enabled on FMC

**Update failed:**
- Check FMC logs for detailed errors
- Verify user has Policy Configuration permissions
- Ensure no other users are editing the policy

## Security Notes

- Script only reads and updates logging settings
- Does not modify rule logic or objects
- Changes are pending until deployed
- Always test in lab environment first

## Related Files

- `lib/fmc_client.py` - Core API client
- `examples/03_access_policies.py` - Policy management examples
- `examples/05_device_management.py` - Deployment examples
- `SECURITY_BEST_PRACTICES.md` - Security guidelines
