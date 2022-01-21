import argparse
import yaml
import sys
from azure.core import credentials
from deployer import create_all_vm, make_rg_if_does_not_exist, setup_eventhub_connect, setup_tcp_connect
from azure.identity import DefaultAzureCredential
import os

def run_deployment(args):
    VNET_NAME = "VNET-Sprinternship"
    SUBNET_NAME = "SUBNET-Sprinternship"
    IP_NAME = "IPName-Sprinternship"
    IP_CONFIG_NAME = "IpConfigName-Sprinternship"
    NIC_NAME = "NICName-Sprinternship"
    NAMESPACE_NAME = "NameSpace-Sprinternship"
    STORAGE_ACCOUNT_NAME = "Sprinternship-Storage"
    LOCATION = "South Central US"
    RETENTION_IN_DAYS = "4"
    PARTITION_COUNT = "4"
    credential = DefaultAzureCredential()
    subscription_id = os.environ["SUBSCRIPTION_ID"]
    nsg_name = "NSG-Sprinternship"
    
    if args.replica * len(args.workload_names) != len(args.configs):
        raise RuntimeError('Length of workloads does not match length of config or eventhubs!')
    
    configs = []
    for replica in range(args.replica):
        configs.append([])
        for workload in range(len(args.workload_names)):
            configs[replica].append(args.configs[(replica * len(args.workload_names)) + workload])
    
    make_rg_if_does_not_exist(subscription_id, args.resource_group, credential, args.location)
    print("Creation of Resource Group - COMPLETED\n")
    
    list_of_ip_addresses = create_all_vm(args.workload_names, args.workload_paths, configs, args.location, credential, args.resource_group, args.key_vault, 
                   os.environ['OBJECT_ID'], VNET_NAME, SUBNET_NAME, IP_NAME, IP_CONFIG_NAME, NIC_NAME, subscription_id, nsg_name, num_retries=3, 
                   replica=args.replica if hasattr(args, 'replica') else 1)
    print(list_of_ip_addresses)
    print("Creation of the Workloads - COMPLETED\n")
    
    first_priv_ip_address_list = []
    for j in range(args.replica):
        first_priv_ip_address_list.append(list_of_ip_addresses[j][1][0])
    
    if args.connection == "EventHubs":
        eventhub_list = setup_eventhub_connect(credential, args.resource_group, NAMESPACE_NAME, args.eventhub_names, STORAGE_ACCOUNT_NAME, subscription_id, LOCATION, RETENTION_IN_DAYS, PARTITION_COUNT)
        temp_list = []
        for j in range(len(eventhub_list)):
            temp_list.append('topic'+str(j))
            temp_list.append(eventhub_list[j])
        dict = ConvertToDictionary(temp_list)
        #take in configs paths
        configs_list = args.configs
        for i in range(len(configs_list)):
            with open(configs_list[i], 'a+') as file:
                documents = yaml.dump(dict, file)
        print("Creation of Multiple Topics in the EventHub Namespace - COMPLETED")
        
    elif args.connection == "TCP":
        connection_pub_ip = setup_tcp_connect(first_priv_ip_address_list, VNET_NAME, SUBNET_NAME, args.resource_group, credential, args.key_vault, nsg_name)
        print("Creation of the TCP Endpoint - COMPLETED")
        print(f"The TCP Connection Endpoint Public Ip Address: {connection_pub_ip}\n")
        
    print("All Resources Ready\n")

def ConvertToDictionary(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct

def deployer():
    parser = argparse.ArgumentParser(prog='deployer')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='Additional help')
    parser_deploy = subparsers.add_parser(
        'deploy', aliases=['d'], help='Deploy help')

    compute_choices = ['AKS', 'VM']
    connection_choices = ["EventHubs", "TCP"]
    parser_deploy.add_argument("compute", type=str, choices=compute_choices)
    parser_deploy.add_argument("connection", type=str, choices=connection_choices)
    parser_deploy.set_defaults(func=run_deployment)

    parser_deploy.add_argument('resource_group', type=str)
    parser_deploy.add_argument('location', type=str)
    parser_deploy.add_argument("--workload_paths", nargs="+")
    parser_deploy.add_argument("--workload_names", nargs="+")
    parser_deploy.add_argument('key_vault', type=str)
    parser_deploy.add_argument("--configs", nargs="+")
    parser_deploy.add_argument("--replica",type=int)
    parser_deploy.add_argument("--eventhub_names", nargs="+")

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
        sys.exit(1)
    args.func(args)   
if __name__ == '__main__':
    deployer()



