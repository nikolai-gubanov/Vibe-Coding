"""
Example 1: Authentication and Basic Operations

Demonstrates:
- Connecting to FMC
- Authenticating
- Token management
- Using context manager
- Retrieving system information
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.fmc_client import FMCClient
from config.fmc_config import FMCConfig


def basic_authentication():
    """Basic authentication example."""
    print("=" * 60)
    print("Example 1: Basic Authentication")
    print("=" * 60)
    
    # Initialize client
    client = FMCClient()
    
    # Authenticate
    if client.authenticate():
        print(f"\n✓ Successfully authenticated to FMC")
        print(f"  Domain UUID: {client.domain_uuid}")
        print(f"  Token: {client.token[:20]}...")
        
        # Logout when done
        client.logout()
        print("\n✓ Logged out successfully")
    else:
        print("\n✗ Authentication failed")


def context_manager_example():
    """Using context manager for automatic cleanup."""
    print("\n" + "=" * 60)
    print("Example 2: Context Manager Usage")
    print("=" * 60)
    
    # Context manager automatically handles auth and logout
    with FMCClient() as client:
        print("\n✓ Automatically authenticated")
        
        # Get system information
        system_info = client.get("info/serverversion")
        
        if system_info:
            print("\nFMC System Information:")
            for item in system_info.get('items', []):
                print(f"  Version: {item.get('serverVersion')}")
                print(f"  Build: {item.get('build')}")
                print(f"  Type: {item.get('type')}")
        
    print("\n✓ Automatically logged out")


def get_domain_info():
    """Retrieve domain information."""
    print("\n" + "=" * 60)
    print("Example 3: Domain Information")
    print("=" * 60)
    
    with FMCClient() as client:
        # Get domains
        domains = client.get("info/domain")
        
        if domains:
            print("\nAvailable Domains:")
            for item in domains.get('items', []):
                print(f"  Name: {item.get('name')}")
                print(f"  UUID: {item.get('uuid')}")
                print(f"  Type: {item.get('type')}")
                print()


def token_refresh_example():
    """Demonstrate automatic token refresh."""
    print("\n" + "=" * 60)
    print("Example 4: Token Refresh (Automatic)")
    print("=" * 60)
    
    client = FMCClient()
    client.authenticate()
    
    print(f"\n✓ Initial authentication")
    print(f"  Token expiry: {client.token_expiry}")
    
    # Simulate token near expiry
    import time
    original_expiry = client.token_expiry
    client.token_expiry = time.time() + 30  # Expire in 30 seconds
    
    print(f"\n⚠ Simulating token near expiry...")
    
    # Make a request - should automatically refresh token
    system_info = client.get("info/serverversion")
    
    if system_info:
        print(f"\n✓ Token automatically refreshed")
        print(f"  New token expiry: {client.token_expiry}")
    
    client.logout()


def error_handling_example():
    """Demonstrate error handling."""
    print("\n" + "=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    with FMCClient() as client:
        # Try to get non-existent object
        result = client.get("object/networks/invalid-uuid")
        
        if result is None:
            print("\n✓ Error handled gracefully")
            print("  The client automatically logs errors and returns None")


def main():
    """Run all authentication examples."""
    try:
        basic_authentication()
        context_manager_example()
        get_domain_info()
        token_refresh_example()
        error_handling_example()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
