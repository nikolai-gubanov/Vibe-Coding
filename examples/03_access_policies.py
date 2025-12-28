"""
Example 3: Access Control Policy Management

Demonstrates:
- Creating access control policies
- Managing access rules
- Adding rules to policies
- Retrieving policy configurations
- Policy deployment
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.fmc_client import FMCClient
from typing import List, Dict, Optional


class AccessPolicyManager:
    """Manager for FMC access control policies."""
    
    def __init__(self, client: FMCClient):
        self.client = client
    
    def create_policy(self, name: str, default_action: str = "BLOCK", 
                     description: str = "") -> dict:
        """
        Create an access control policy.
        
        Args:
            name: Policy name
            default_action: Default action (BLOCK, TRUST, NETWORK_DISCOVERY, etc.)
            description: Policy description
        
        Returns:
            Created policy data
        """
        data = {
            "name": name,
            "type": "AccessPolicy",
            "defaultAction": {
                "action": default_action
            },
            "description": description
        }
        
        self.client.logger.info(f"Creating access policy: {name}")
        return self.client.post("policy/accesspolicies", data)
    
    def get_all_policies(self) -> List[dict]:
        """Get all access control policies."""
        self.client.logger.info("Retrieving all access policies")
        return self.client.get_all_pages("policy/accesspolicies")
    
    def get_policy_by_name(self, name: str) -> Optional[dict]:
        """Get policy by name."""
        policies = self.client.get("policy/accesspolicies", 
                                  params={"filter": f"name:{name}"})
        
        if policies and policies.get('items'):
            return policies['items'][0]
        return None
    
    def create_access_rule(self, policy_id: str, rule_data: dict) -> dict:
        """
        Create an access rule in a policy.
        
        Args:
            policy_id: Parent policy UUID
            rule_data: Rule configuration
        
        Returns:
            Created rule data
        """
        endpoint = f"policy/accesspolicies/{policy_id}/accessrules"
        self.client.logger.info(f"Creating access rule in policy {policy_id}")
        return self.client.post(endpoint, rule_data)
    
    def get_policy_rules(self, policy_id: str) -> List[dict]:
        """Get all rules in a policy."""
        endpoint = f"policy/accesspolicies/{policy_id}/accessrules"
        self.client.logger.info(f"Retrieving rules for policy {policy_id}")
        return self.client.get_all_pages(endpoint)
    
    def build_allow_rule(self, name: str, source_networks: List[dict],
                        dest_networks: List[dict], source_ports: List[dict] = None,
                        dest_ports: List[dict] = None, enabled: bool = True) -> dict:
        """
        Build an ALLOW access rule configuration.
        
        Args:
            name: Rule name
            source_networks: List of source network objects
            dest_networks: List of destination network objects
            source_ports: List of source port objects (optional)
            dest_ports: List of destination port objects (optional)
            enabled: Whether rule is enabled
        
        Returns:
            Rule configuration dictionary
        """
        rule = {
            "name": name,
            "type": "AccessRule",
            "action": "ALLOW",
            "enabled": enabled,
            "sourceNetworks": {
                "objects": source_networks
            },
            "destinationNetworks": {
                "objects": dest_networks
            }
        }
        
        if source_ports:
            rule["sourcePorts"] = {"objects": source_ports}
        
        if dest_ports:
            rule["destinationPorts"] = {"objects": dest_ports}
        
        return rule
    
    def build_block_rule(self, name: str, source_networks: List[dict],
                        dest_networks: List[dict], enabled: bool = True) -> dict:
        """Build a BLOCK access rule configuration."""
        return {
            "name": name,
            "type": "AccessRule",
            "action": "BLOCK",
            "enabled": enabled,
            "sourceNetworks": {
                "objects": source_networks
            },
            "destinationNetworks": {
                "objects": dest_networks
            }
        }


def example_create_policy():
    """Create an access control policy."""
    print("=" * 60)
    print("Example 1: Creating Access Control Policy")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = AccessPolicyManager(client)
        
        print("\n1. Creating new access policy...")
        policy = manager.create_policy(
            name="Lab_Access_Policy",
            default_action="BLOCK",
            description="Access policy for lab environment"
        )
        
        if policy:
            print(f"  ✓ Policy created successfully")
            print(f"    Name: {policy.get('name')}")
            print(f"    ID: {policy.get('id')}")
            print(f"    Default Action: {policy.get('defaultAction', {}).get('action')}")
        else:
            print(f"  ✗ Policy creation failed")


def example_list_policies():
    """List all access control policies."""
    print("\n" + "=" * 60)
    print("Example 2: Listing Access Control Policies")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = AccessPolicyManager(client)
        
        print("\nRetrieving all policies...")
        policies = manager.get_all_policies()
        
        print(f"\nFound {len(policies)} policies:")
        for policy in policies:
            print(f"\n  • {policy.get('name')}")
            print(f"    ID: {policy.get('id')}")
            print(f"    Type: {policy.get('type')}")
            print(f"    Default Action: {policy.get('defaultAction', {}).get('action')}")


def example_create_rules():
    """Create access rules in a policy."""
    print("\n" + "=" * 60)
    print("Example 3: Creating Access Rules")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = AccessPolicyManager(client)
        
        # Find the policy
        print("\n1. Finding policy...")
        policy = manager.get_policy_by_name("Lab_Access_Policy")
        
        if not policy:
            print("  ✗ Policy not found. Create it first.")
            return
        
        print(f"  ✓ Found policy: {policy.get('name')}")
        policy_id = policy.get('id')
        
        # Get network objects for rules (example assumes they exist)
        print("\n2. Retrieving network objects...")
        
        # For this example, we'll use "any" objects
        # In practice, you'd retrieve specific network objects
        
        # Create a simple allow rule
        print("\n3. Creating ALLOW rule for web traffic...")
        
        rule_data = {
            "name": "Allow_Web_Traffic",
            "type": "AccessRule",
            "action": "ALLOW",
            "enabled": True,
            "sendEventsToFMC": True,
            "logBegin": False,
            "logEnd": True
        }
        
        rule = manager.create_access_rule(policy_id, rule_data)
        
        if rule:
            print(f"  ✓ Rule created successfully")
            print(f"    Name: {rule.get('name')}")
            print(f"    Action: {rule.get('action')}")
        
        # Create a block rule
        print("\n4. Creating BLOCK rule for suspicious traffic...")
        
        block_rule_data = {
            "name": "Block_Suspicious_Traffic",
            "type": "AccessRule",
            "action": "BLOCK",
            "enabled": True,
            "sendEventsToFMC": True,
            "logBegin": True,
            "logEnd": True
        }
        
        block_rule = manager.create_access_rule(policy_id, block_rule_data)
        
        if block_rule:
            print(f"  ✓ Block rule created successfully")
            print(f"    Name: {block_rule.get('name')}")


def example_list_rules():
    """List all rules in a policy."""
    print("\n" + "=" * 60)
    print("Example 4: Listing Policy Rules")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = AccessPolicyManager(client)
        
        # Find the policy
        print("\n1. Finding policy...")
        policy = manager.get_policy_by_name("Lab_Access_Policy")
        
        if not policy:
            print("  ✗ Policy not found")
            return
        
        print(f"  ✓ Found policy: {policy.get('name')}")
        
        # Get all rules
        print("\n2. Retrieving all rules...")
        rules = manager.get_policy_rules(policy.get('id'))
        
        print(f"\nFound {len(rules)} rules:")
        for idx, rule in enumerate(rules, 1):
            print(f"\n  {idx}. {rule.get('name')}")
            print(f"     Action: {rule.get('action')}")
            print(f"     Enabled: {rule.get('enabled')}")
            print(f"     ID: {rule.get('id')}")


def example_complex_rule_with_objects():
    """Create a complex rule with specific network and port objects."""
    print("\n" + "=" * 60)
    print("Example 5: Complex Rule with Objects")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = AccessPolicyManager(client)
        
        print("\n1. Finding policy...")
        policy = manager.get_policy_by_name("Lab_Access_Policy")
        
        if not policy:
            print("  ✗ Policy not found")
            return
        
        # This example shows the structure - you'd need actual object IDs
        print("\n2. Creating rule with specific objects...")
        print("   (Note: This requires existing network/port objects)")
        
        # Example structure - replace with actual object references
        rule_data = {
            "name": "Allow_Internal_to_DMZ_Web",
            "type": "AccessRule",
            "action": "ALLOW",
            "enabled": True,
            "sourceNetworks": {
                "objects": [
                    # {"type": "Network", "id": "internal-network-uuid", "name": "Internal_Network"}
                ]
            },
            "destinationNetworks": {
                "objects": [
                    # {"type": "Network", "id": "dmz-network-uuid", "name": "DMZ_Network"}
                ]
            },
            "destinationPorts": {
                "objects": [
                    # {"type": "ProtocolPortObject", "id": "http-port-uuid", "name": "HTTP"}
                ]
            },
            "logBegin": False,
            "logEnd": True,
            "sendEventsToFMC": True
        }
        
        print("\n  Rule structure prepared:")
        print(f"    Name: {rule_data['name']}")
        print(f"    Action: {rule_data['action']}")
        print(f"    Note: Add actual object references to create this rule")


def main():
    """Run all access policy examples."""
    try:
        print("\n⚠ WARNING: These examples will create policies in your FMC")
        print("Make sure you're connected to a test/lab environment\n")
        
        example_create_policy()
        example_list_policies()
        example_create_rules()
        example_list_rules()
        example_complex_rule_with_objects()
        
        print("\n" + "=" * 60)
        print("Access policy examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
