# Import the needed credential and management objects from the libraries.
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os

print(f"Provisioning a virtual machine...some operations might take a minute or two.")

credential = DefaultAzureCredential()

subscription_id = os.environ["SUBSCRIPTION_ID"]




# Step 1: Provision a resource group
resource_client = ResourceManagementClient(credential, subscription_id)

RESOURCE_GROUP_NAME = "PythonAzureExample-VM-rg-steve12" # rename
LOCATION = "westus2"

# Provision the resource group.
rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
    {
        "location": LOCATION
    }
)


print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")



# get this working here!!!!

# Step 2: provision a virtual network

# A virtual machine requires a network interface client (NIC). A NIC requires
# a virtual network and subnet along with an IP address. Therefore we must provision
# these downstream components first, then provision the NIC, after which we
# can provision the VM.

# Network and IP address names
VNET_NAME = "python-example-vnet"
SUBNET_NAME = "python-example-subnet"
IP_NAME = "python-example-ip"
IP_CONFIG_NAME = "python-example-ip-config"
NIC_NAME = "python-example-nic"

# Obtain the management object for networks
network_client = NetworkManagementClient(credential, subscription_id)
nsg = network_client.network_security_groups.begin_create_or_update(RESOURCE_GROUP_NAME, "testnsg", {'location': 'westus2',
                                                                                                     "security_rules": [
          {
            "name": "sshrule",
            "properties": {
              "protocol": "*",
              "sourceAddressPrefix": "*",
              "destinationAddressPrefix": "*",
              "access": "Allow",
              "destinationPortRange": "22",
              "sourcePortRange": "*",
              "priority": 130,
              "direction": "Inbound"
            }
          }
        ]})
nsg_id = nsg.result().as_dict()['id']
print('\nid is ' + str(nsg_id))

# Provision the virtual network and wait for completion
poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {
            "address_prefixes": ["10.0.0.0/16"]
        }
    }
)

vnet_result = poller.result()

print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")


# Step 3: Provision the subnet and wait for completion
poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME, 
    VNET_NAME, SUBNET_NAME,
    { "address_prefix": "10.0.0.0/24" }
)
subnet_result = poller.result()

print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

# Step 4: Provision an IP address and wait for completion
poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": { "name": "Standard" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)

ip_address_result = poller.result()

print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

# Step 5: Provision the network interface client
poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
    NIC_NAME, 
    {
        "location": LOCATION,
        "ip_configurations": [ {
            "name": IP_CONFIG_NAME,
            "subnet": { "id": subnet_result.id },
            "public_ip_address": {"id": ip_address_result.id }
        }],
        "network_security_group": {'id': f'{nsg_id}'}
    }
)

nic_result = poller.result()

print(f"Provisioned network interface client {nic_result.name}")

# Step 6: Provision the virtual machine

# Obtain the management object for virtual machines
compute_client = ComputeManagementClient(credential, subscription_id)

VM_NAME = "ExampleVM"
USERNAME = "azureuser"

print(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")

# Provision the VM specifying only minimal arguments, which defaults to an Ubuntu 18.04 VM
# on a Standard DS1 v2 plan with a public IP address and a default virtual network/subnet.

poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
    {
        "location": LOCATION,
        "storage_profile": {
            "image_reference": {
                "publisher": 'Canonical',
                "offer": "UbuntuServer",
                "sku": "16.04.0-LTS",
                "version": "latest"
            }
        },
        "hardware_profile": {
            "vm_size": "Standard_DS1_v2"
        },
        "os_profile": {
            "computer_name": VM_NAME,
            "admin_username": USERNAME,
            "linuxConfiguration": {
            "ssh": {
              "publicKeys": [
                {
                  "path": f"/home/{USERNAME}/.ssh/authorized_keys",
                  "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDj2RY58T10C60a8q0sKdu1YiwecMXdGsj8M0aOOcIBm2jMydG8kLUuIt9qva7HE8FHSVJZqyg49PAvdO+wIUVRPNZYQNTSdc0GpoXv8gfajkQjBI3Uj87Q6uJDueeFPcQnlTBF3hLTHc2JYaSL+o6OFG6xT1El9/NFdUm9yrOIaVbfukqD46PGXwxvDArONemoU/XisxT0Eu4C2pD47bYVilDTCCCwGa2UfrZg1hE6jlNV2bIE+3drT6qFprQ2SOYQQUOCFcjghIUOs9r1K1IOUk/fme+vJLGhN45+VNO/K7fTTTw0RZhAebz6tw7bA504T0bGCgWSP27b83g2NKC6qOrD7t3yqzmD9WdcQKqzuGr1DgflwJtglfgfwH0jnnlWTy4cng5f/SOfPzf4fisORXdSkBAyfvMcFPAZnDSbtD1vpVgQ7QsbhD0Jw0gX2nsJK+0tGfMLrrAvtKrCSfzkRGkY6JWBROGWAFPMlXu9KPBDv3Xg4MBgfRR11v7EfXZ/xftXRVqHUCAd7arkU9GPQSiqNfEtAfkxska+YJFy4E2syu639vHsfgUb5a/yfS58MXgIsk1c5ZtOAaVb3QnlRJsjJKHAaZsHVcfTRnwdIiMpULXJoPT4Mpih2SSVWEV38kHIh8Rn2+X7MVzdR1Ae5sNlhzIFSBnYShp3bxL8cQ== stevens@microsoft.com"
                }
              ]
            },
            "disablePasswordAuthentication": True
          }
        },
        "network_profile": {
            "network_interfaces": [{
                "id": nic_result.id,
            }]
        }        
    }
)

vm_result = poller.result()

print(f"Provisioned virtual machine {vm_result.name}")


