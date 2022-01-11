import subprocess
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError
import os
import subprocess

def setup_tcp_connect(vnet_name, subnet_name, rg_name, credential, key_vault, nsg_name):
    #create vm with public ip that connects to same vnet and subvnets that the other vms connect to, return public ip address
    location = "westus2"
    vm_name = "amyVM12"
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
    FILE = ".\\eng\\grc\\difi_to_udp.py"
    scp_str = f"scp -i {vm_name}_key.pem -o StrictHostKeyChecking=no {FILE} azureuser@{ip_address_result.ip_address}:/home/azureuser/"
    
    subprocess.run(scp_str)

    return ip_address_result.ip_address

if __name__ == '__main__':
    credential = DefaultAzureCredential()
    setup_tcp_connect("python-example-vnet", "python-example-subnet", "PythonAzureExample-VM-rg-amy4", credential, "amyvault4", "testnsg")
