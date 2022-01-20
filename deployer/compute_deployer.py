from datetime import time
from ntpath import realpath
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError
import os
import subprocess
import time
import yaml

def create_vm(vm_name, location, credential, rg_name, key_vault, object_id,
            vnet_name, subnet_name, ip_name, ip_config_name, nic_name, subscription_id, nsg_name):

    VNET_NAME = vnet_name
    SUBNET_NAME = subnet_name
    IP_NAME = vm_name + ip_name
    IP_CONFIG_NAME = vm_name + ip_config_name
    NIC_NAME = vm_name + nic_name

    compute_client = ComputeManagementClient(credential, subscription_id)

    try:
        vm_result = compute_client.virtual_machines.get(rg_name, vm_name=vm_name)
        print("vm already exists!")

        raise RuntimeError()
    except ResourceNotFoundError as e:
        print('resource does not exist, making vm')


    # Obtain the management object for networks
    network_client = NetworkManagementClient(credential, subscription_id)
    nsg = network_client.network_security_groups.begin_create_or_update(rg_name, nsg_name, {'location': location,
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
          },
          {
            "name": "TCP",
            "properties": {
              "protocol": "TCP",
              "sourceAddressPrefix": "*",
              "destinationAddressPrefix": "*",
              "access": "Allow",
              "destinationPortRange": "*",
              "sourcePortRange": "*",
              "priority": 100,
              "direction": "Inbound"
            }
          }
        ]})
    nsg_id = nsg.result().as_dict()['id']


    make_vnet = False
    try:
        vnet_result = network_client.virtual_networks.get(rg_name, VNET_NAME)
    except ResourceNotFoundError as e:
        print('resource does not exist, making vent')
        make_vnet = True

    if make_vnet:
        poller = network_client.virtual_networks.begin_create_or_update(rg_name,
        VNET_NAME,
        {
            "location": location,
            "address_space": {
                "address_prefixes": ["10.0.0.0/16"]
            }
        }
        )
        vnet_result = poller.result()

    print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

    make_subnet = False
    try:
        subnet_result = network_client.subnets.get(rg_name, VNET_NAME, SUBNET_NAME)
    except ResourceNotFoundError as e:
        print('resource does not exist, making subnet')
        make_subnet = True

    # Step 3: Provision the subnet and wait for completion
    if make_subnet:
        poller = network_client.subnets.begin_create_or_update(rg_name,
            VNET_NAME, SUBNET_NAME,
            { "address_prefix": "10.0.0.0/24" }
        )
        subnet_result = poller.result()

    print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

    # Step 4: Provision an IP address and wait for completion
    poller = network_client.public_ip_addresses.begin_create_or_update(rg_name,
    IP_NAME,
    {
        "location": location,
        "sku": { "name": "Standard" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)

    ip_address_result = poller.result()

    print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

    # Step 5: Provision the network interface client
    poller = network_client.network_interfaces.begin_create_or_update(rg_name, NIC_NAME,
    {
        "location": location,
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


    key = rsa.generate_private_key(backend=crypto_default_backend(),public_exponent=65537,key_size=2048)
    private_key = key.private_bytes(crypto_serialization.Encoding.PEM,crypto_serialization.PrivateFormat.PKCS8,crypto_serialization.NoEncryption())
    public_key = key.public_key().public_bytes(crypto_serialization.Encoding.OpenSSH,crypto_serialization.PublicFormat.OpenSSH)

    TENANT_ID = os.environ.get("AZURE_TENANT_ID", None)
    CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", None)
    CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", None)

    keyvault_client = KeyVaultManagementClient(credential, subscription_id)

    make_vault = False
    try:
        does_exist = keyvault_client.vaults.get(
            rg_name,
            key_vault
        )
    except ResourceNotFoundError as e:
        print('resource does not exist, making vault')
        make_vault = True

    if make_vault:
        #Create vault
        vault = keyvault_client.vaults.begin_create_or_update(
            rg_name,
            key_vault,
            {
            "location": "eastus",
            "properties": {
                "tenant_id": TENANT_ID,
                "sku": {
                "family": "A",
                "name": "standard"
                },
                "access_policies": [
                {
                    "tenant_id": TENANT_ID,
                    "object_id": object_id,
                    "permissions": {
                    "keys": [
                        "encrypt",
                        "decrypt",
                        "wrapKey",
                        "unwrapKey",
                        "sign",
                        "verify",
                        "get",
                        "list",
                        "create",
                        "update",
                        "import",
                        "delete",
                        "backup",
                        "restore",
                        "recover",
                        "purge"
                    ],
                    "secrets": [
                        "get",
                        "list",
                        "set",
                        "delete",
                        "backup",
                        "restore",
                        "recover",
                        "purge"
                    ],
                    "certificates": [
                        "get",
                        "list",
                        "delete",
                        "create",
                        "import",
                        "update",
                        "managecontacts",
                        "getissuers",
                        "listissuers",
                        "setissuers",
                        "deleteissuers",
                        "manageissuers",
                        "recover",
                        "purge"
                    ]
                    }
                }, {
                    "applicationId": None,
                    "objectId": object_id,
                    "permissions": {
                    "certificates": None,
                    "keys": None,
                    "secrets": [
                    "set",
                    "list",
                    "purge",
                    "get",
                    "backup",
                    "recover",
                    "restore",
                    "delete"
                    ],
                    "storage": None
                    },
                    "tenantId": TENANT_ID
                    }
                ],
                "enabled_for_deployment": True,
                "enabled_for_disk_encryption": False,
                "enabled_for_template_deployment": True
            }
            }
        ).result()


    secret_client = SecretClient(vault_url=f"https://{key_vault}.vault.azure.net/", credential=credential)
    set_secret = secret_client.set_secret(f"{vm_name}-private-key", private_key)
    set_secret = secret_client.set_secret(f"{vm_name}-public-key", public_key)

    USERNAME = "azureuser"

    print(f"Provisioning virtual machine {vm_name} this operation might take a few minutes.")

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
                "vm_size": "Standard_F4"
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
    vm = compute_client.virtual_machines.instance_view(rg_name, vm_name)

    vm_status = vm.statuses[1].display_status

    print(f"Provisioned virtual machine {vm_result.name} {vm_status}")


    private_ip_address_result = network_client.network_interfaces.get(rg_name,NIC_NAME).ip_configurations[0].private_ip_address

    return ip_address_result.ip_address, private_key, private_ip_address_result




def create_all_vm(workload_names, workload_paths, workload_configs, location, credential, rg_name, key_vault, obj_id, VNET_NAME, SUBNET_NAME, IP_NAME,
                    IP_CONFIG_NAME, NIC_NAME, subscription_id, nsg_name, num_retries=3, replica=1):

    oot_module_script=os.path.join(os.path.dirname(__file__),'..','eng','scripts','install_main.py')
    list_of_addresses = []
    #copy creds over to VM
    cmd_creds =  f'export AZURE_TENANT_ID={os.environ["AZURE_TENANT_ID"]}; ' + f'export AZURE_CLIENT_ID={os.environ["AZURE_CLIENT_ID"]}; '\
        + f'export AZURE_CLIENT_SECRET={os.environ["AZURE_CLIENT_SECRET"]}; ' + f'export AZURE_SUBSCRIPTION_ID={os.environ["SUBSCRIPTION_ID"]}'

    FILE = os.path.join(os.path.dirname(__file__),'runner.py')
    LAUNCH = os.path.join(os.path.dirname(__file__),'run.py')

    #step 1 workload
    for rep_count in range(replica):
        public_ip_address = []
        private_ip_address = []
        for i in range(len(workload_names)):
            ip_address, private_key, private_ip_address_result = create_vm(workload_names[i] + str(rep_count),
                                                                          location, credential, rg_name, key_vault,
                                                                          obj_id, VNET_NAME, SUBNET_NAME, IP_NAME,
                                                                          IP_CONFIG_NAME, NIC_NAME, subscription_id, nsg_name)
            f = open(f"{workload_names[i] + str(rep_count)}_key.pem", "w")
            f.write(private_key.decode("utf-8"))
            f.close()

            public_ip_address.append(ip_address)
            private_ip_address.append(private_ip_address_result)

        for i in range(len(workload_names)):
                
            PY_FILE = workload_paths[i]
            YAML_FILE = workload_configs[rep_count][i]
            print("yaml file is \n")
            print(YAML_FILE)
            with open(YAML_FILE) as f:
                dict = yaml.load(f, Loader=yaml.FullLoader)
            print(f'dict is {dict}')
            if 'forwarding_ip' in dict and i != len(workload_names) - 1:
                dict['forwarding_ip'] = private_ip_address[i + 1]
            with open(YAML_FILE, 'w') as f:
                yaml.dump(dict, f)
            print(f"yaml loading done for {PY_FILE}")
            w_name = workload_names[i] + str(rep_count)
            scp_str=['scp', '-i', f'{w_name}_key.pem', '-o', 'StrictHostKeyChecking=no', f'{PY_FILE}', f'{YAML_FILE}', f'{FILE}', f'{LAUNCH}', f'{oot_module_script}', f'azureuser@{public_ip_address[i]}:/home/azureuser']
            print(scp_str)

            value_returned = subprocess.run(scp_str)

            if value_returned.returncode != 0:
                for _ in range(num_retries):
                    if value_returned.returncode != 0:
                        time.sleep(30)
                        value_returned = subprocess.run(scp_str)
                    else:
                        print("good ...")
                        break
            print("\n")
            print(workload_paths[i])
            print(workload_configs[rep_count][i])
            
            instance_name_path = os.path.split(workload_paths[i])[-1]
            instance_yml = os.path.split(workload_configs[rep_count][i])[-1]
            print(instance_name_path)
            print(instance_yml)
            cmd = f'ssh -i {w_name}_key.pem azureuser@{public_ip_address[i]} \"{cmd_creds}; python3 install_main.py && tmux new-session -d -s work_sessions \; send-keys \'python3 run.py {instance_name_path} {instance_yml}\' Enter\"'
            subprocess.check_call(cmd, shell=True)
            
        list_of_addresses.append((public_ip_address, private_ip_address))

    return list_of_addresses

if __name__ == '__main__':

    workloads = ['newworkload1', 'newworkload2']
    workload_paths = ["helloworld.py", "helloworld.py"]
    print(f"Provisioning a virtual machine...some operations might take a minute or two.")

    credential = DefaultAzureCredential()

    subscription_id = os.environ["SUBSCRIPTION_ID"]

    #Step 1: Provision a resource group
    resource_client = ResourceManagementClient(credential, subscription_id)
    VM_NAME = "vmName2"

    RESOURCE_GROUP_NAME = "PythonAzureExample-VM-rg-samanvitha1" # rename
    LOCATION = "westus2"
    VAULT = "vaultsamanvitha1"

    #Provision the resource group.
    rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
      {
        "location": LOCATION
    }
    )

    VNET_NAME = "python-example-vnet"
    SUBNET_NAME = "python-example-subnet"
    IP_NAME = "python-example-ip"
    IP_CONFIG_NAME = "python-example-ip-config"
    NIC_NAME = "python-example-nic"


    name = VM_NAME
    location = LOCATION
    rg_name = RESOURCE_GROUP_NAME
    key_vault = VAULT
    nsg_name = "testnsg"

    obj_id = os.environ['OBJECT_ID']


    #workloads_paths = ""

    ip_adresses = create_all_vm(workloads, workload_paths, location, credential, rg_name, key_vault, obj_id, VNET_NAME, SUBNET_NAME, IP_NAME, IP_CONFIG_NAME, NIC_NAME, subscription_id, nsg_name, num_retries=3)
    print(ip_adresses)

    print("Completed!")





