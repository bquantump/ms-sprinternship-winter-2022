from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import ResourceNotFoundError

def make_rg_if_does_not_exist(subscription_id, rg_name, credential, location):
    #credential = DefaultAzureCredential()
    resource_client = ResourceManagementClient(credential, subscription_id)
    try:
        _ = resource_client.resource_groups.get(rg_name)
        print("resource group already exists!")
        return None
    except ResourceNotFoundError as e:
        print('resource group does not exist, making resource group')
        rg_result = resource_client.resource_groups.create_or_update(rg_name, {
            'location': location
        }
        )