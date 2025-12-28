"""
Example 6: Bulk Operations and Automation

Demonstrates:
- Bulk object creation from CSV/lists
- Error handling and rollback
- Progress tracking
- Export/import configurations
- Automated reporting
"""

import sys
import os
import csv
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.fmc_client import FMCClient
from lib.utils import chunk_list, validate_ip_address, validate_ip_network


class BulkOperationsManager:
    """Manager for bulk operations in FMC."""
    
    def __init__(self, client: FMCClient):
        self.client = client
        self.success_count = 0
        self.failure_count = 0
        self.failures = []
    
    def reset_counters(self):
        """Reset success/failure counters."""
        self.success_count = 0
        self.failure_count = 0
        self.failures = []
    
    def bulk_create_hosts(self, host_list: List[Tuple[str, str, str]]) -> dict:
        """
        Create multiple host objects.
        
        Args:
            host_list: List of (name, ip, description) tuples
        
        Returns:
            Summary of operations
        """
        self.reset_counters()
        
        self.client.logger.info(f"Starting bulk creation of {len(host_list)} hosts")
        
        for name, ip, description in host_list:
            # Validate IP
            if not validate_ip_address(ip):
                self.client.logger.warning(f"Invalid IP for {name}: {ip}")
                self.failure_count += 1
                self.failures.append((name, "Invalid IP address"))
                continue
            
            # Create host
            data = {
                "name": name,
                "type": "Host",
                "value": ip,
                "description": description
            }
            
            result = self.client.post("object/hosts", data)
            
            if result:
                self.success_count += 1
                self.client.logger.info(f"✓ Created: {name}")
            else:
                self.failure_count += 1
                self.failures.append((name, "API request failed"))
                self.client.logger.error(f"✗ Failed: {name}")
        
        return {
            "total": len(host_list),
            "success": self.success_count,
            "failed": self.failure_count,
            "failures": self.failures
        }
    
    def bulk_create_networks(self, network_list: List[Tuple[str, str, str]]) -> dict:
        """
        Create multiple network objects.
        
        Args:
            network_list: List of (name, network, description) tuples
        
        Returns:
            Summary of operations
        """
        self.reset_counters()
        
        self.client.logger.info(f"Starting bulk creation of {len(network_list)} networks")
        
        for name, network, description in network_list:
            # Validate network
            if not validate_ip_network(network):
                self.client.logger.warning(f"Invalid network for {name}: {network}")
                self.failure_count += 1
                self.failures.append((name, "Invalid network format"))
                continue
            
            # Create network
            data = {
                "name": name,
                "type": "Network",
                "value": network,
                "description": description
            }
            
            result = self.client.post("object/networks", data)
            
            if result:
                self.success_count += 1
                self.client.logger.info(f"✓ Created: {name}")
            else:
                self.failure_count += 1
                self.failures.append((name, "API request failed"))
                self.client.logger.error(f"✗ Failed: {name}")
        
        return {
            "total": len(network_list),
            "success": self.success_count,
            "failed": self.failure_count,
            "failures": self.failures
        }
    
    def export_network_objects(self, output_file: str = "network_objects.csv"):
        """Export all network objects to CSV."""
        self.client.logger.info("Exporting network objects...")
        
        # Get all hosts
        hosts = self.client.get_all_pages("object/hosts")
        
        # Get all networks
        networks = self.client.get_all_pages("object/networks")
        
        # Write to CSV
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Type', 'Name', 'Value', 'Description'])
            
            for host in hosts:
                writer.writerow([
                    'Host',
                    host.get('name'),
                    host.get('value'),
                    host.get('description', '')
                ])
            
            for network in networks:
                writer.writerow([
                    'Network',
                    network.get('name'),
                    network.get('value'),
                    network.get('description', '')
                ])
        
        total = len(hosts) + len(networks)
        self.client.logger.info(f"Exported {total} objects to {output_file}")
        return total
    
    def import_from_csv(self, csv_file: str) -> dict:
        """
        Import network objects from CSV.
        
        CSV Format: Type,Name,Value,Description
        """
        self.reset_counters()
        
        self.client.logger.info(f"Importing from {csv_file}")
        
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                obj_type = row['Type']
                name = row['Name']
                value = row['Value']
                description = row.get('Description', '')
                
                # Determine endpoint and validate
                if obj_type == 'Host':
                    if not validate_ip_address(value):
                        self.failure_count += 1
                        self.failures.append((name, "Invalid IP"))
                        continue
                    endpoint = "object/hosts"
                elif obj_type == 'Network':
                    if not validate_ip_network(value):
                        self.failure_count += 1
                        self.failures.append((name, "Invalid network"))
                        continue
                    endpoint = "object/networks"
                else:
                    self.failure_count += 1
                    self.failures.append((name, f"Unknown type: {obj_type}"))
                    continue
                
                # Create object
                data = {
                    "name": name,
                    "type": obj_type,
                    "value": value,
                    "description": description
                }
                
                result = self.client.post(endpoint, data)
                
                if result:
                    self.success_count += 1
                else:
                    self.failure_count += 1
                    self.failures.append((name, "API request failed"))
        
        return {
            "success": self.success_count,
            "failed": self.failure_count,
            "failures": self.failures
        }


def example_bulk_host_creation():
    """Create multiple hosts from a list."""
    print("=" * 60)
    print("Example 1: Bulk Host Creation")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = BulkOperationsManager(client)
        
        # Define hosts to create
        hosts = [
            ("Server_01", "10.10.1.1", "Application server 01"),
            ("Server_02", "10.10.1.2", "Application server 02"),
            ("Server_03", "10.10.1.3", "Application server 03"),
            ("Server_04", "10.10.1.4", "Application server 04"),
            ("Server_05", "10.10.1.5", "Application server 05"),
            ("DB_Primary", "10.10.2.10", "Primary database server"),
            ("DB_Secondary", "10.10.2.11", "Secondary database server"),
            ("LoadBalancer", "10.10.3.100", "Main load balancer"),
        ]
        
        print(f"\nCreating {len(hosts)} host objects...")
        
        summary = manager.bulk_create_hosts(hosts)
        
        print(f"\n{'='*60}")
        print(f"Bulk Creation Summary:")
        print(f"  Total: {summary['total']}")
        print(f"  ✓ Success: {summary['success']}")
        print(f"  ✗ Failed: {summary['failed']}")
        
        if summary['failures']:
            print(f"\nFailed objects:")
            for name, reason in summary['failures']:
                print(f"  • {name}: {reason}")


def example_bulk_network_creation():
    """Create multiple networks from a list."""
    print("\n" + "=" * 60)
    print("Example 2: Bulk Network Creation")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = BulkOperationsManager(client)
        
        # Define networks to create
        networks = [
            ("Branch_Office_LAN_1", "192.168.10.0/24", "Branch office 1 LAN"),
            ("Branch_Office_LAN_2", "192.168.20.0/24", "Branch office 2 LAN"),
            ("Branch_Office_LAN_3", "192.168.30.0/24", "Branch office 3 LAN"),
            ("Data_Center_VLAN100", "10.100.0.0/24", "Data center VLAN 100"),
            ("Data_Center_VLAN200", "10.200.0.0/24", "Data center VLAN 200"),
            ("Cloud_VPC_Subnet", "172.31.0.0/16", "AWS VPC subnet"),
        ]
        
        print(f"\nCreating {len(networks)} network objects...")
        
        summary = manager.bulk_create_networks(networks)
        
        print(f"\n{'='*60}")
        print(f"Bulk Creation Summary:")
        print(f"  Total: {summary['total']}")
        print(f"  ✓ Success: {summary['success']}")
        print(f"  ✗ Failed: {summary['failed']}")


def example_export_objects():
    """Export existing objects to CSV."""
    print("\n" + "=" * 60)
    print("Example 3: Export Objects to CSV")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = BulkOperationsManager(client)
        
        output_file = "fmc_network_objects_export.csv"
        
        print(f"\nExporting network objects to {output_file}...")
        total = manager.export_network_objects(output_file)
        
        print(f"\n✓ Exported {total} objects successfully")
        print(f"  File: {output_file}")


def example_import_from_csv():
    """Import objects from CSV file."""
    print("\n" + "=" * 60)
    print("Example 4: Import from CSV")
    print("=" * 60)
    
    # Create sample CSV first
    sample_csv = "sample_import.csv"
    
    print(f"\n1. Creating sample CSV: {sample_csv}")
    with open(sample_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Name', 'Value', 'Description'])
        writer.writerow(['Host', 'Import_Host_1', '10.20.1.1', 'Imported host 1'])
        writer.writerow(['Host', 'Import_Host_2', '10.20.1.2', 'Imported host 2'])
        writer.writerow(['Network', 'Import_Net_1', '10.30.0.0/24', 'Imported network 1'])
    
    print(f"  ✓ Sample CSV created")
    
    print(f"\n2. Importing objects from CSV...")
    
    with FMCClient() as client:
        manager = BulkOperationsManager(client)
        
        summary = manager.import_from_csv(sample_csv)
        
        print(f"\n{'='*60}")
        print(f"Import Summary:")
        print(f"  ✓ Success: {summary['success']}")
        print(f"  ✗ Failed: {summary['failed']}")
        
        if summary['failures']:
            print(f"\nFailed imports:")
            for name, reason in summary['failures']:
                print(f"  • {name}: {reason}")


def example_chunked_operations():
    """Process large operations in chunks."""
    print("\n" + "=" * 60)
    print("Example 5: Chunked Operations")
    print("=" * 60)
    
    # Simulate a large list of objects
    large_host_list = [
        (f"Bulk_Host_{i:03d}", f"10.50.{i//250}.{i%250}", f"Auto-generated host {i}")
        for i in range(1, 101)  # Create 100 hosts
    ]
    
    print(f"\nProcessing {len(large_host_list)} objects in chunks...")
    
    # Split into chunks of 10
    chunks = chunk_list(large_host_list, 10)
    
    print(f"  Split into {len(chunks)} chunks of 10 objects each")
    
    with FMCClient() as client:
        manager = BulkOperationsManager(client)
        
        total_success = 0
        total_failed = 0
        
        for idx, chunk in enumerate(chunks, 1):
            print(f"\n  Processing chunk {idx}/{len(chunks)}...")
            
            summary = manager.bulk_create_hosts(chunk)
            total_success += summary['success']
            total_failed += summary['failed']
            
            print(f"    ✓ {summary['success']} success, ✗ {summary['failed']} failed")
        
        print(f"\n{'='*60}")
        print(f"Overall Summary:")
        print(f"  Total processed: {len(large_host_list)}")
        print(f"  ✓ Total success: {total_success}")
        print(f"  ✗ Total failed: {total_failed}")


def example_error_handling_and_rollback():
    """Demonstrate error handling and rollback logic."""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling & Rollback")
    print("=" * 60)
    
    with FMCClient() as client:
        print("\n1. Creating test objects...")
        
        # Create some objects with intentional errors
        test_data = [
            ("Valid_Host_1", "10.60.1.1", "Valid host"),
            ("Invalid_Host", "999.999.999.999", "Invalid IP"),  # Will fail
            ("Valid_Host_2", "10.60.1.2", "Valid host"),
        ]
        
        created_objects = []
        
        for name, ip, desc in test_data:
            if not validate_ip_address(ip):
                print(f"  ✗ Validation failed: {name} ({ip})")
                
                # Rollback: delete previously created objects
                if created_objects:
                    print(f"\n2. Rolling back {len(created_objects)} created objects...")
                    for obj_id in created_objects:
                        client.delete(f"object/hosts/{obj_id}")
                        print(f"    Deleted: {obj_id}")
                
                print("\n  ⚠ Operation aborted due to validation error")
                return
            
            # Create the object
            data = {
                "name": name,
                "type": "Host",
                "value": ip,
                "description": desc
            }
            
            result = client.post("object/hosts", data)
            
            if result:
                created_objects.append(result.get('id'))
                print(f"  ✓ Created: {name}")
            else:
                print(f"  ✗ Failed: {name}")
                # Rollback logic would go here
        
        print(f"\n  ✓ Successfully created {len(created_objects)} objects")


def main():
    """Run all bulk operation examples."""
    try:
        print("\n⚠ WARNING: These examples will create many objects in your FMC")
        print("Make sure you're connected to a test/lab environment\n")
        
        example_bulk_host_creation()
        example_bulk_network_creation()
        example_export_objects()
        example_import_from_csv()
        # example_chunked_operations()  # Uncomment to create 100 objects
        example_error_handling_and_rollback()
        
        print("\n" + "=" * 60)
        print("Bulk operation examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
