import subprocess
from azure.identity import DefaultAzureCredential
from azure.mgmt.eventhub import EventHubManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from azure.keyvault.secrets import SecretClient
import os
import subprocess
import time

from deployer.utils import make_difi_to_udp

#from deployer.compute_deployer import RESOURCE_GROUP_NAME

def setup_eventhub_connect(credential, rg_name, namespace_name, eventhub_names, storage_account_name, subscription_id, location, retention_in_days, partition_count):
    

    eventhub_client = EventHubManagementClient(credential=credential, subscription_id=subscription_id)
    storage_client = StorageManagementClient(credential=credential, subscription_id=subscription_id)

    # Create StorageAccount
    storage_account = storage_client.storage_accounts.begin_create(
        rg_name,
        storage_account_name,
        {
          "sku": {
            "name": "Standard_LRS"
          },
          "kind": "StorageV2",
          "location": "eastus"
        }
    )
    storage_account_result = storage_account.result()

    # Create Namespace
    namespace = eventhub_client.namespaces.begin_create_or_update(
        rg_name,
        namespace_name,
        {
          "sku": {
            "name": "Standard",
            "tier": "Standard"
          },
          "location": location,
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
    )
    namespace_result = namespace.result()

    #create Eventhub
    BODY = {"message_retention_in_days": retention_in_days,
          "partition_count": partition_count,
          "status": "Active",
          "capture_description": {
            "enabled": True,
            "encoding": "Avro",
            "interval_in_seconds": "120",
            "size_limit_in_bytes": "10485763",
            "destination": {
              "name": "EventHubArchive.AzureBlockBlob",
              "storage_account_resource_id": "/subscriptions/" + subscription_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Storage/storageAccounts/" + storage_account_name + "",
              "blob_container": "container",
              "archive_name_format": "{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}"
            }
          }
    }

    for j in range(len(eventhub_names)):
        eventhub = eventhub_client.event_hubs.create_or_update(
            rg_name,
            namespace_name,
            eventhub_names[j],
            BODY)

    return eventhub_names
    
def setup_tcp_connect(first_priv_ip_address_list, vnet_name, subnet_name, rg_name, credential, key_vault, nsg_name):
    #create vm with public ip that connects to same vnet and subvnets that the other vms connect to, return public ip address
    location = "westus2"
    vm_name = "connectvmname5"
    subscription_id = os.environ["SUBSCRIPTION_ID"]
    ip_config_name = vm_name + "ipaddress"

    nic_name = "python-example-nic" + vm_name

    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    poller = network_client.public_ip_addresses.begin_create_or_update(rg_name,
    ip_config_name,
    {
        "location": location,
        "sku": { "name": "Standard" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
    )

    ip_address_result = poller.result()

    print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

    subnet_result = network_client.subnets.get(rg_name, vnet_name, subnet_name)
    nsg_result = network_client.network_security_groups.get(rg_name, nsg_name)

    nsg_id = nsg_result.id

    # Step 5: Provision the network interface client
    poller = network_client.network_interfaces.begin_create_or_update(rg_name, nic_name,
    {
        "location": location,
        "ip_configurations": [ {
            "name": ip_config_name,
            "subnet": { "id": subnet_result.id },
            "public_ip_address": {"id": ip_address_result.id }
        }],
        "network_security_group": {'id': f'{nsg_id}'}
    }
    )

    nic_result = poller.result()

    print(f"Provisioned network interface client {nic_result.name}")


    key = rsa.generate_private_key(backend=crypto_default_backend(),public_exponent=65537,key_size=2048)
    private_key = key.private_bytes(crypto_serialization.Encoding.PEM,crypto_serialization.PrivateFormat.PKCS8,crypto_serialization.NoEncryption())
    public_key = key.public_key().public_bytes(crypto_serialization.Encoding.OpenSSH,crypto_serialization.PublicFormat.OpenSSH)

    secret_client = SecretClient(vault_url=f"https://{key_vault}.vault.azure.net/", credential=credential)
    set_secret = secret_client.set_secret(f"{vm_name}-private-key", private_key)
    set_secret = secret_client.set_secret(f"{vm_name}-public-key", public_key)

    USERNAME = "azureuser"

    # Provision the VM specifying only minimal arguments, which defaults to an Ubuntu 18.04 VM
    # on a Standard DS1 v2 plan with a public IP address and a default virtual network/subnet.

    poller = compute_client.virtual_machines.begin_create_or_update(rg_name, vm_name,
        {
            "location": location,
            "storage_profile": {
                "image_reference": {
                    "id": f"/subscriptions/{subscription_id}/resourceGroups/az-mi-sdk-rg/providers/Microsoft.Compute/galleries/azsdrsharedgallery/images/azsdrdevvm"
                }
            },
            "hardware_profile": {
                "vm_size": "Standard_DS1_v2"
            },
            "os_profile": {
                "computer_name": vm_name,
                "admin_username": USERNAME,
                "linuxConfiguration": {
                "ssh": {
                "publicKeys": [
                    {
                    "path": f"/home/{USERNAME}/.ssh/authorized_keys",
                    "keyData": public_key.decode("utf-8")
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

    f = open(f"{vm_name}_key.pem", "w")
    f.write(private_key.decode("utf-8"))
    f.close()


    make_difi_to_udp(first_priv_ip_address_list, ip_address_result.ip_address)
    FILE = "difi_to_udp.py"
    oot_module_script=os.path.join(os.path.dirname(__file__), '..','eng','scripts','install_main.py')

    scp_str = ['scp', '-i', f'{vm_name}_key.pem', '-o', 'StrictHostKeyChecking=no', f'{FILE}', f'{oot_module_script}', f'azureuser@{ip_address_result.ip_address}:/home/azureuser/']
    value_returned = subprocess.run(scp_str)

    if value_returned.returncode != 0:
            for j in range(3):
                if value_returned.returncode != 0:
                    time.sleep(30)
                    value_returned = subprocess.run(scp_str)
                else:
                    break

    run_command_parameters = {
            'command_id': 'RunShellScript', # For linux, don't change it
            'script': [
                f'cd /home/azureuser; python3 install_main.py d3c9ea2; python3 {FILE} > workload_log.txt &'
                ]
            }

    compute_client = ComputeManagementClient(credential=credential,subscription_id=subscription_id)

    poller = compute_client.virtual_machines.begin_run_command(
            rg_name,
            vm_name,
            run_command_parameters)

    result = poller.result()

    print(result.value[0].message)

    return ip_address_result.ip_address

if __name__ == '__main__':
    credential = DefaultAzureCredential()
    subscription_id = os.environ["SUBSCRIPTION_ID"]
    RESOURCE_GROUP_NAME = "samanvitha6"
    #eventhub_names = "python-example-eventhub"
    NAMESPACE_NAME = "python-example-namespace"
    STORAGE_ACCOUNT_NAME = "storagesamanvitha1"
    LOCATION = "South Central US"
    RETENTION_IN_DAYS = "4"
    PARTITION_COUNT = "4"

    eventhub_names = ["eventhub_numb0", "eventhub_numb1"]
    
    setup_eventhub_connect(credential, RESOURCE_GROUP_NAME, NAMESPACE_NAME, eventhub_names, STORAGE_ACCOUNT_NAME, subscription_id, LOCATION, RETENTION_IN_DAYS, PARTITION_COUNT)

    #setup_tcp_connect("python-example-vnet", "python-example-subnet", "PythonAzureExample-VM-rg-amy4", credential, "amyvault4", "testnsg")
