"""
Example 4: Device Management

Demonstrates:
- Listing managed devices
- Retrieving device details
- Deploying configuration to devices
- Monitoring deployment status
- Device health checks
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.fmc_client import FMCClient
from typing import List, Optional


class DeviceManager:
    """Manager for FMC device operations."""
    
    def __init__(self, client: FMCClient):
        self.client = client
    
    def get_all_devices(self) -> List[dict]:
        """Get all managed devices."""
        self.client.logger.info("Retrieving all devices")
        return self.client.get_all_pages("devices/devicerecords")
    
    def get_device_by_name(self, name: str) -> Optional[dict]:
        """Get device by name."""
        devices = self.client.get("devices/devicerecords",
                                 params={"filter": f"name:{name}"})
        
        if devices and devices.get('items'):
            return devices['items'][0]
        return None
    
    def get_device_details(self, device_id: str) -> Optional[dict]:
        """Get detailed device information."""
        self.client.logger.info(f"Retrieving details for device {device_id}")
        return self.client.get(f"devices/devicerecords/{device_id}")
    
    def deploy_to_device(self, device_id: str, force_deploy: bool = False,
                        ignore_warning: bool = True) -> Optional[dict]:
        """
        Deploy pending changes to a device.
        
        Args:
            device_id: Device UUID
            force_deploy: Force deployment even if no changes detected
            ignore_warning: Ignore deployment warnings
        
        Returns:
            Deployment job information
        """
        data = {
            "type": "DeploymentRequest",
            "version": int(time.time()),
            "forceDeploy": force_deploy,
            "ignoreWarning": ignore_warning,
            "deviceList": [device_id]
        }
        
        self.client.logger.info(f"Initiating deployment to device {device_id}")
        return self.client.post("deployment/deploymentrequests", data)
    
    def get_deployment_status(self, deployment_id: str) -> Optional[dict]:
        """Get deployment job status."""
        self.client.logger.info(f"Checking deployment status for {deployment_id}")
        return self.client.get(f"deployment/deploymentrequests/{deployment_id}")
    
    def get_pending_deployments(self) -> List[dict]:
        """Get all devices with pending deployments."""
        self.client.logger.info("Checking for pending deployments")
        
        devices = self.get_all_devices()
        pending = []
        
        for device in devices:
            metadata = device.get('metadata', {})
            if metadata.get('deploymentStatus') == 'PENDING':
                pending.append(device)
        
        return pending
    
    def wait_for_deployment(self, deployment_id: str, timeout: int = 300,
                          poll_interval: int = 10) -> bool:
        """
        Wait for deployment to complete.
        
        Args:
            deployment_id: Deployment job UUID
            timeout: Maximum wait time in seconds
            poll_interval: Time between status checks
        
        Returns:
            True if deployment succeeded, False otherwise
        """
        elapsed = 0
        
        while elapsed < timeout:
            status = self.get_deployment_status(deployment_id)
            
            if not status:
                return False
            
            # Check deployment state
            deploy_state = status.get('deploymentState')
            
            if deploy_state == 'DEPLOYED':
                self.client.logger.info("Deployment completed successfully")
                return True
            elif deploy_state in ['FAILED', 'ABORTED']:
                self.client.logger.error(f"Deployment {deploy_state.lower()}")
                return False
            
            self.client.logger.info(f"Deployment in progress... ({deploy_state})")
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        self.client.logger.warning("Deployment timeout reached")
        return False


def example_list_devices():
    """List all managed devices."""
    print("=" * 60)
    print("Example 1: Listing Managed Devices")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = DeviceManager(client)
        
        print("\nRetrieving all devices...")
        devices = manager.get_all_devices()
        
        print(f"\nFound {len(devices)} managed devices:")
        for device in devices:
            print(f"\n  • {device.get('name')}")
            print(f"    Type: {device.get('type')}")
            print(f"    Model: {device.get('model')}")
            print(f"    IP: {device.get('hostName')}")
            print(f"    SW Version: {device.get('sw_version', 'N/A')}")
            
            # Deployment status
            metadata = device.get('metadata', {})
            deploy_status = metadata.get('deploymentStatus', 'UNKNOWN')
            print(f"    Deployment Status: {deploy_status}")


def example_device_details():
    """Get detailed device information."""
    print("\n" + "=" * 60)
    print("Example 2: Device Details")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = DeviceManager(client)
        
        # Get first device
        devices = manager.get_all_devices()
        
        if not devices:
            print("\n  ✗ No devices found")
            return
        
        device = devices[0]
        print(f"\n1. Retrieving details for: {device.get('name')}")
        
        details = manager.get_device_details(device.get('id'))
        
        if details:
            print(f"\n  Device Information:")
            print(f"    Name: {details.get('name')}")
            print(f"    Type: {details.get('type')}")
            print(f"    Model: {details.get('model')}")
            print(f"    Serial: {details.get('serialNumber', 'N/A')}")
            print(f"    Hostname: {details.get('hostName')}")
            
            # Access policy
            policy = details.get('accessPolicy', {})
            if policy:
                print(f"    Access Policy: {policy.get('name', 'None')}")
            
            # Interfaces (if available)
            if 'interfaces' in details:
                interfaces = details['interfaces']
                print(f"\n  Interfaces: {len(interfaces)}")


def example_check_pending_deployments():
    """Check for pending deployments."""
    print("\n" + "=" * 60)
    print("Example 3: Checking Pending Deployments")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = DeviceManager(client)
        
        print("\nChecking for devices with pending changes...")
        pending = manager.get_pending_deployments()
        
        if pending:
            print(f"\nFound {len(pending)} devices with pending changes:")
            for device in pending:
                print(f"\n  • {device.get('name')}")
                print(f"    ID: {device.get('id')}")
                metadata = device.get('metadata', {})
                print(f"    Status: {metadata.get('deploymentStatus')}")
        else:
            print("\n  ✓ No pending deployments")


def example_deploy_configuration():
    """Deploy configuration to a device."""
    print("\n" + "=" * 60)
    print("Example 4: Deploying Configuration")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = DeviceManager(client)
        
        # Check for pending deployments
        print("\n1. Checking for devices with pending changes...")
        pending = manager.get_pending_deployments()
        
        if not pending:
            print("  ✓ No pending deployments found")
            print("\n  Note: Make policy/object changes first to test deployment")
            return
        
        device = pending[0]
        print(f"\n2. Found device with pending changes: {device.get('name')}")
        print(f"   Device ID: {device.get('id')}")
        
        # Ask for confirmation (in production, you'd want this)
        print("\n3. Initiating deployment...")
        print("   ⚠ WARNING: This will deploy changes to the device")
        
        # Uncomment to actually deploy:
        # deployment = manager.deploy_to_device(device.get('id'))
        # 
        # if deployment:
        #     print(f"  ✓ Deployment initiated")
        #     print(f"    Deployment ID: {deployment.get('id')}")
        #     
        #     # Wait for completion
        #     print("\n4. Waiting for deployment to complete...")
        #     success = manager.wait_for_deployment(deployment.get('id'))
        #     
        #     if success:
        #         print("  ✓ Deployment completed successfully")
        #     else:
        #         print("  ✗ Deployment failed or timed out")
        
        print("\n  (Deployment code commented out for safety)")


def example_bulk_deployment():
    """Deploy to multiple devices."""
    print("\n" + "=" * 60)
    print("Example 5: Bulk Deployment")
    print("=" * 60)
    
    with FMCClient() as client:
        manager = DeviceManager(client)
        
        print("\n1. Finding all devices with pending changes...")
        pending = manager.get_pending_deployments()
        
        if not pending:
            print("  ✓ No pending deployments")
            return
        
        print(f"\n2. Found {len(pending)} devices with pending changes")
        
        # In practice, you might deploy to all at once or in batches
        print("\n3. Deployment strategy:")
        print("   • Deploy to devices one by one")
        print("   • Monitor each deployment")
        print("   • Handle failures gracefully")
        
        # Example structure (commented for safety):
        # for device in pending:
        #     print(f"\n   Deploying to: {device.get('name')}")
        #     deployment = manager.deploy_to_device(device.get('id'))
        #     
        #     if deployment:
        #         success = manager.wait_for_deployment(deployment.get('id'))
        #         if success:
        #             print(f"     ✓ Success")
        #         else:
        #             print(f"     ✗ Failed")
        
        print("\n  (Deployment code commented out for safety)")


def main():
    """Run all device management examples."""
    try:
        example_list_devices()
        example_device_details()
        example_check_pending_deployments()
        example_deploy_configuration()
        example_bulk_deployment()
        
        print("\n" + "=" * 60)
        print("Device management examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
