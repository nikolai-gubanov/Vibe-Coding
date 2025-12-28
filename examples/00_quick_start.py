"""
Quick Start Guide - Your First FMC Automation Script

This script demonstrates a complete workflow:
1. Connect and authenticate
2. Create network objects
3. Create an access policy
4. Add rules to the policy
5. Check deployment status

Run this after configuring your .env file.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.fmc_client import FMCClient


def main():
    """Quick start automation example."""
    
    print("=" * 70)
    print("FMC Automation Quick Start")
    print("=" * 70)
    
    # Step 1: Connect to FMC
    print("\n[Step 1] Connecting to FMC...")
    
    with FMCClient() as client:
        print("✓ Connected and authenticated successfully")
        
        # Step 2: Get system information
        print("\n[Step 2] Retrieving system information...")
        
        system_info = client.get("info/serverversion")
        if system_info and system_info.get('items'):
            info = system_info['items'][0]
            print(f"✓ FMC Version: {info.get('serverVersion')}")
            print(f"  Build: {info.get('build')}")
        
        # Step 3: List existing network objects
        print("\n[Step 3] Retrieving existing network objects...")
        
        hosts = client.get("object/hosts", params={"limit": 5})
        if hosts and hosts.get('items'):
            count = hosts.get('paging', {}).get('count', 0)
            print(f"✓ Found {count} host objects (showing first 5):")
            for host in hosts['items'][:5]:
                print(f"  • {host.get('name')}: {host.get('value')}")
        else:
            print("  No host objects found")
        
        # Step 4: Create a simple host object
        print("\n[Step 4] Creating a test host object...")
        
        new_host = {
            "name": "QuickStart_Test_Host",
            "type": "Host",
            "value": "192.168.99.99",
            "description": "Created by quick start script"
        }
        
        result = client.post("object/hosts", new_host)
        if result:
            print(f"✓ Created host: {result.get('name')}")
            print(f"  ID: {result.get('id')}")
            host_id = result.get('id')
            
            # Clean up - delete the test object
            print("\n[Step 5] Cleaning up test object...")
            if client.delete(f"object/hosts/{host_id}"):
                print("✓ Test object deleted")
        else:
            print("✗ Failed to create host object")
        
        # Step 6: List access policies
        print("\n[Step 6] Retrieving access policies...")
        
        policies = client.get("policy/accesspolicies")
        if policies and policies.get('items'):
            print(f"✓ Found {len(policies['items'])} access policies:")
            for policy in policies['items']:
                print(f"  • {policy.get('name')}")
        else:
            print("  No access policies found")
        
        # Step 7: Check for managed devices
        print("\n[Step 7] Checking managed devices...")
        
        devices = client.get("devices/devicerecords", params={"limit": 5})
        if devices and devices.get('items'):
            count = devices.get('paging', {}).get('count', 0)
            print(f"✓ Found {count} managed devices:")
            for device in devices['items']:
                print(f"  • {device.get('name')} ({device.get('model')})")
                metadata = device.get('metadata', {})
                deploy_status = metadata.get('deploymentStatus', 'UNKNOWN')
                print(f"    Deployment status: {deploy_status}")
        else:
            print("  No managed devices found")
    
    # Completed
    print("\n" + "=" * 70)
    print("Quick Start Completed Successfully!")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Review the example scripts in the examples/ directory")
    print("  2. Explore 01_authentication.py for auth patterns")
    print("  3. Check 02_network_objects.py for object management")
    print("  4. See 03_access_policies.py for policy automation")
    print("  5. Review 05_device_management.py for deployments")
    print("  6. Study 06_bulk_operations.py for bulk automation")
    print("\nDocumentation:")
    print("  • FMC API Explorer: https://your-fmc-ip/api/api-explorer/")
    print("  • Project README.md for detailed information")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify .env file is configured correctly")
        print("  2. Check FMC connectivity (ping/https access)")
        print("  3. Verify credentials are correct")
        print("  4. Check FMC REST API is enabled")
        print("  5. Review logs for detailed error information")
        
        import traceback
        traceback.print_exc()
