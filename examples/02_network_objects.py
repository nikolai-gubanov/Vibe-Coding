"""
Example 2: Network Object Management

Demonstrates:
- Creating network objects (hosts, networks, ranges)
- Retrieving network objects
- Updating network objects
- Deleting network objects
- Bulk operations
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.fmc_client import FMCClient
from lib.utils import validate_ip_address, validate_ip_network


class NetworkObjectManager:
    """Manager for FMC network objects."""
    
    def __init__(self, client: FMCClient):
        self.client = client
    
    def create_host(self, name: str, ip_address: str, description: str = "") -> dict:
        """
        Create a host network object.
        
        Args:
            name: Object name
            ip_address: IPv4 address
            description: Optional description
        
        Returns:
            Created object data
        """
        if not validate_ip_address(ip_address):
            raise ValueError(f"Invalid IP address: {ip_address}")
        
        data = {
            "name": name,
            "type": "Host",
            "value": ip_address,
            "description": description
        }
        
        self.client.logger.info(f"Creating host object: {name} ({ip_address})")
        return self.client.post("object/hosts", data)
    
    def create_network(self, name: str, network: str, description: str = "") -> dict:
        """
        Create a network object.
        
        Args:
            name: Object name
            network: Network in CIDR notation (e.g., '192.168.1.0/24')
            description: Optional description
        
        Returns:
            Created object data
        """
        if not validate_ip_network(network):
            raise ValueError(f"Invalid network: {network}")
        
        data = {
            "name": name,
            "type": "Network",
            "value": network,
            "description": description
        }
        
        self.client.logger.info(f"Creating network object: {name} ({network})")
        return self.client.post("object/networks", data)
    
    def create_range(self, name: str, start_ip: str, end_ip: str, description: str = "") -> dict:
        """
        Create an IP range object.
        
        Args:
            name: Object name
            start_ip: Starting IP address
            end_ip: Ending IP address
            description: Optional description
        
        Returns:
            Created object data
        """
        if not validate_ip_address(start_ip) or not validate_ip_address(end_ip):
            raise ValueError("Invalid IP addresses in range")
        
        data = {
            "name": name,
            "type": "Range",
            "value": f"{start_ip}-{end_ip}",
            "description": description
        }
        
        self.client.logger.info(f"Creating range object: {name} ({start_ip}-{end_ip})")
        return self.client.post("object/ranges", data)
    
    def get_all_hosts(self) -> list:
        """Get all host objects."""
        self.client.logger.info("Retrieving all host objects")
        return self.client.get_all_pages("object/hosts")
    
    def get_all_networks(self) -> list:
        """Get all network objects."""
        self.client.logger.info("Retrieving all network objects")
        return self.client.get_all_pages("object/networks")
    
    def get_host_by_name(self, name: str) -> dict:
        """Get host object by name."""
        hosts = self.client.get("object/hosts", params={"filter": f"name:{name}"})
        
        if hosts and hosts.get('items'):
            return hosts['items'][0]
        return None
    
    def get_network_by_name(self, name: str) -> dict:
        """Get network object by name."""
        networks = self.client.get("object/networks", params={"filter": f"name:{name}"})
        
        if networks and networks.get('items'):
            return networks['items'][0]
        return None
    
    def update_host(self, host_id: str, name: str, ip_address: str, description: str = "") -> dict:
        """Update existing host object."""
        data = {
            "id": host_id,
            "name": name,
            "type": "Host",
            "value": ip_address,
            "description": description
        }
        
        self.client.logger.info(f"Updating host object: {name}")
        return self.client.put(f"object/hosts/{host_id}", data)
    
    def delete_host(self, host_id: str) -> bool:
        """Delete host object."""
        self.client.logger.info(f"Deleting host object: {host_id}")
        return self.client.delete(f"object/hosts/{host_id}")
    
    def delete_network(self, network_id: str) -> bool:
        """Delete network object."""
        self.client.logger.info(f"Deleting network object: {network_id}")
        return self.client.delete(f"object/networks/{network_id}")


def example_create_objects():
    """Create various network objects."""
    print("=" * 60)
    print("Example 1: Creating Network Objects")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = NetworkObjectManager(client)
        
        # Create host objects
        print("\n1. Creating host objects...")
        hosts = [
            ("Web_Server_1", "10.1.1.10", "Production web server"),
            ("Database_Server", "10.1.2.20", "Main database server"),
            ("DNS_Server", "10.1.3.30", "Internal DNS server")
        ]
        
        for name, ip, desc in hosts:
            result = manager.create_host(name, ip, desc)
            if result:
                print(f"  ✓ Created host: {name} ({ip})")
            else:
                print(f"  ✗ Failed to create: {name}")
        
        # Create network objects
        print("\n2. Creating network objects...")
        networks = [
            ("DMZ_Network", "192.168.100.0/24", "DMZ zone"),
            ("Internal_Network", "10.0.0.0/8", "Internal corporate network"),
            ("Guest_WiFi", "172.16.50.0/24", "Guest wireless network")
        ]
        
        for name, net, desc in networks:
            result = manager.create_network(name, net, desc)
            if result:
                print(f"  ✓ Created network: {name} ({net})")
            else:
                print(f"  ✗ Failed to create: {name}")
        
        # Create range object
        print("\n3. Creating IP range object...")
        result = manager.create_range(
            "DHCP_Pool",
            "192.168.1.100",
            "192.168.1.200",
            "DHCP address pool"
        )
        if result:
            print(f"  ✓ Created range: DHCP_Pool")


def example_retrieve_objects():
    """Retrieve and display network objects."""
    print("\n" + "=" * 60)
    print("Example 2: Retrieving Network Objects")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = NetworkObjectManager(client)
        
        # Get all hosts
        print("\n1. Retrieving all host objects...")
        hosts = manager.get_all_hosts()
        print(f"  Found {len(hosts)} host objects:")
        for host in hosts[:5]:  # Show first 5
            print(f"    - {host.get('name')}: {host.get('value')}")
        
        # Get specific object by name
        print("\n2. Retrieving specific host by name...")
        host = manager.get_host_by_name("Web_Server_1")
        if host:
            print(f"  ✓ Found: {host.get('name')}")
            print(f"    ID: {host.get('id')}")
            print(f"    Value: {host.get('value')}")
            print(f"    Description: {host.get('description')}")


def example_update_objects():
    """Update existing network objects."""
    print("\n" + "=" * 60)
    print("Example 3: Updating Network Objects")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = NetworkObjectManager(client)
        
        # Find object to update
        print("\n1. Finding object to update...")
        host = manager.get_host_by_name("Web_Server_1")
        
        if host:
            print(f"  ✓ Found: {host.get('name')}")
            
            # Update the object
            print("\n2. Updating object...")
            updated = manager.update_host(
                host.get('id'),
                "Web_Server_1",
                "10.1.1.15",  # New IP
                "Production web server - Updated IP"
            )
            
            if updated:
                print(f"  ✓ Updated successfully")
                print(f"    New IP: {updated.get('value')}")


def example_delete_objects():
    """Delete network objects."""
    print("\n" + "=" * 60)
    print("Example 4: Deleting Network Objects")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = NetworkObjectManager(client)
        
        # Find and delete object
        print("\n1. Finding object to delete...")
        host = manager.get_host_by_name("DNS_Server")
        
        if host:
            print(f"  ✓ Found: {host.get('name')}")
            
            print("\n2. Deleting object...")
            if manager.delete_host(host.get('id')):
                print(f"  ✓ Deleted successfully")
            else:
                print(f"  ✗ Deletion failed")


def example_bulk_create():
    """Bulk create network objects from list."""
    print("\n" + "=" * 60)
    print("Example 5: Bulk Object Creation")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = NetworkObjectManager(client)
        
        # List of servers to create
        servers = [
            ("App_Server_1", "10.2.1.10"),
            ("App_Server_2", "10.2.1.11"),
            ("App_Server_3", "10.2.1.12"),
            ("App_Server_4", "10.2.1.13"),
            ("App_Server_5", "10.2.1.14")
        ]
        
        print(f"\nCreating {len(servers)} host objects...")
        success_count = 0
        
        for name, ip in servers:
            result = manager.create_host(name, ip, f"Application server {name}")
            if result:
                success_count += 1
                print(f"  ✓ {name}")
            else:
                print(f"  ✗ {name}")
        
        print(f"\n✓ Created {success_count}/{len(servers)} objects")


def main():
    """Run all network object examples."""
    try:
        # Note: Uncomment examples as needed
        # These examples create real objects in FMC
        
        print("\n⚠ WARNING: These examples will create objects in your FMC")
        print("Make sure you're connected to a test/lab environment\n")
        
        example_create_objects()
        example_retrieve_objects()
        # example_update_objects()  # Uncomment to test updates
        # example_delete_objects()   # Uncomment to test deletion
        # example_bulk_create()      # Uncomment for bulk creation
        
        print("\n" + "=" * 60)
        print("Network object examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
