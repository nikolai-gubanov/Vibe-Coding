"""
Update Access Control Policy Rules - Logging Configuration

This script updates rules in the "Vibe Coding Demo Policy" to:
- Add "Log at end of connection" for ALLOW rules
- Add "Log at beginning of connection" for BLOCK rules
- Send Connection Events to FMC for all rules
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.fmc_client import FMCClient


def update_policy_logging(client, policy_name="Vibe Coding Demo Policy"):
    """
    Update logging configuration for all rules in the specified policy.
    
    Args:
        client: FMC client instance
        policy_name: Name of the policy to update
    """
    # Step 1: Find the policy
    print(f"\n[Step 1] Finding policy: {policy_name}")
    all_policies = client.get("policy/accesspolicies")
    
    if not all_policies or not all_policies.get('items'):
        print(f"✗ No policies found")
        return False
    
    # Search for the policy by name
    policy = None
    for p in all_policies['items']:
        if p.get('name') == policy_name:
            policy = p
            break
    
    if not policy:
        print(f"✗ Policy '{policy_name}' not found")
        print("\nAvailable policies:")
        for p in all_policies['items']:
            print(f"  • {p.get('name')}")
        return False
    policy_id = policy.get('id')
    print(f"✓ Found policy: {policy.get('name')}")
    print(f"  Policy ID: {policy_id}")
    
    # Step 2: Get all rules in the policy
    print(f"\n[Step 2] Retrieving all rules in policy...")
    endpoint = f"policy/accesspolicies/{policy_id}/accessrules"
    rules = client.get_all_pages(endpoint)
    
    if not rules:
        print("✗ No rules found in policy")
        return False
    
    print(f"✓ Found {len(rules)} rules")
    
    # Step 3: Get full details for each rule (summary doesn't include all fields)
    print(f"\n[Step 3] Retrieving detailed rule information...")
    detailed_rules = []
    for rule in rules:
        rule_id = rule.get('id')
        full_rule = client.get(f"{endpoint}/{rule_id}")
        if full_rule:
            detailed_rules.append(full_rule)
    
    print(f"✓ Retrieved {len(detailed_rules)} detailed rules")
    
    # Step 4: Update each rule
    print(f"\n[Step 4] Updating logging configuration for each rule...")
    
    updated_count = 0
    skipped_count = 0
    failed_count = 0
    
    for idx, rule in enumerate(detailed_rules, 1):
        rule_name = rule.get('name', 'Unnamed Rule')
        rule_id = rule.get('id')
        action = rule.get('action', 'UNKNOWN')
        
        # Debug: Print full rule for first one
        if idx == 1:
            client.logger.debug(f"Sample rule data: {rule}")
        
        print(f"\n  [{idx}/{len(rules)}] {rule_name}")
        print(f"    Action: {action}")
        print(f"    Rule ID: {rule_id[:20]}...")
        
        # Prepare update data
        update_data = {
            "id": rule_id,
            "name": rule.get('name'),
            "type": rule.get('type'),
            "action": action,
            "enabled": rule.get('enabled', True),
            "sendEventsToFMC": True,  # Always send events to FMC
        }
        
        # Copy other important fields
        if 'sourceNetworks' in rule:
            update_data['sourceNetworks'] = rule['sourceNetworks']
        if 'destinationNetworks' in rule:
            update_data['destinationNetworks'] = rule['destinationNetworks']
        if 'sourcePorts' in rule:
            update_data['sourcePorts'] = rule['sourcePorts']
        if 'destinationPorts' in rule:
            update_data['destinationPorts'] = rule['destinationPorts']
        if 'applications' in rule:
            update_data['applications'] = rule['applications']
        if 'urls' in rule:
            update_data['urls'] = rule['urls']
        if 'sourceZones' in rule:
            update_data['sourceZones'] = rule['sourceZones']
        if 'destinationZones' in rule:
            update_data['destinationZones'] = rule['destinationZones']
        if 'vlanTags' in rule:
            update_data['vlanTags'] = rule['vlanTags']
        if 'users' in rule:
            update_data['users'] = rule['users']
        
        # Set logging based on action
        if action == 'ALLOW':
            update_data['logBegin'] = False
            update_data['logEnd'] = True
            print(f"    Logging: End of connection ✓")
        elif action == 'BLOCK':
            update_data['logBegin'] = True
            update_data['logEnd'] = False
            print(f"    Logging: Beginning of connection ✓")
        else:
            # For other actions (TRUST, MONITOR, etc.), keep existing or default
            update_data['logBegin'] = rule.get('logBegin', False)
            update_data['logEnd'] = rule.get('logEnd', False)
            print(f"    Action '{action}' - keeping existing logging settings")
            skipped_count += 1
            continue
        
        # Update the rule
        result = client.put(f"{endpoint}/{rule_id}", update_data)
        
        if result:
            print(f"    ✓ Updated successfully")
            updated_count += 1
        else:
            print(f"    ✗ Update failed")
            failed_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Update Summary:")
    print(f"  Total rules: {len(detailed_rules)}")
    print(f"  ✓ Updated: {updated_count}")
    print(f"  ⊘ Skipped: {skipped_count}")
    print(f"  ✗ Failed: {failed_count}")
    print(f"{'='*60}")
    
    if updated_count > 0:
        print(f"\n⚠ IMPORTANT: Changes have been made to the policy.")
        print(f"   You need to deploy to devices for changes to take effect.")
        print(f"   Go to: Deploy > Deployment or use device management script")
    
    return updated_count > 0


def main():
    """Main execution function."""
    print("=" * 60)
    print("Update Access Control Policy - Logging Configuration")
    print("=" * 60)
    
    try:
        with FMCClient() as client:
            success = update_policy_logging(client, "Vibe Coding Demo Policy")
            
            if success:
                print("\n✓ Policy rules updated successfully!")
                print("\nNext Steps:")
                print("  1. Review changes in FMC UI")
                print("  2. Deploy to managed devices")
                print("  3. Verify logging is working as expected")
            else:
                print("\n⚠ No rules were updated")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
