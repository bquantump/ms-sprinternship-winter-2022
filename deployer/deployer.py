import argparse
import sys
from azure.core import credentials
from deployer import create_all_vm, make_rg_if_does_not_exist, setup_eventhub_connect, setup_tcp_connect
from azure.identity import DefaultAzureCredential
import os
import yaml

def run_deployment(args):
    VNET_NAME = "python-example-vnet"
    SUBNET_NAME = "python-example-subnet"
    IP_NAME = "python-example-ip"
    IP_CONFIG_NAME = "python-example-ip-config"
    NIC_NAME = "python-example-nic"
    EVENTHUB_NAME = "python-example-eventhub"
    NAMESPACE_NAME = "python-example-namespace"
    STORAGE_ACCOUNT_NAME = "storagesamanvitha1"
    LOCATION = "South Central US"
    RETENTION_IN_DAYS = "4"
    PARTITION_COUNT = "4"
    credential = DefaultAzureCredential()
    subscription_id = os.environ["SUBSCRIPTION_ID"]
    nsg_name = "testnsg"
    
    if len(args.workload_names) != len(args.configs) and len(args.workloads_paths) != len(args.configs):
        raise RuntimeError('length of workloads does not match length of config')
    
        

    make_rg_if_does_not_exist(subscription_id, args.resource_group, credential, args.location)
    print("rg making completed!!\n")
    list_of_ip_addresses = create_all_vm(args.workload_names, args.workload_paths, args.configs, args.location, credential, args.resource_group, args.key_vault, 
                   os.environ['OBJECT_ID'], VNET_NAME, SUBNET_NAME, IP_NAME, IP_CONFIG_NAME, NIC_NAME, subscription_id, nsg_name, num_retries=3, 
                   replica=args.replica if hasattr(args, 'replica') else 1)
    print(list_of_ip_addresses)
    print("all vm creation is completed!!\n")
    
    first_priv_ip_address_list = []
    for j in range(args.replica):
        first_priv_ip_address_list.append(list_of_ip_addresses[j][1][0])
    
    forwarding_ip_add = list_of_ip_addresses[0][1][1]
    
    config_path = args.configs[0]
    with open(config_path) as f:
        dict = yaml.load(f, Loader=yaml.FullLoader)
    
    dict['forwarding_ip'] = forwarding_ip_add
    with open(config_path, 'w') as f:
        yaml.dump(dict, f)
    print("yaml loading done!")
    
    if args.coonection == "Eventhubs":
        setup_eventhub_connect(credential, args.resource_group, NAMESPACE_NAME, EVENTHUB_NAME, STORAGE_ACCOUNT_NAME, subscription_id, LOCATION, RETENTION_IN_DAYS, PARTITION_COUNT)
    elif args.coonection == "TCP":
        setup_tcp_connect(first_priv_ip_address_list, VNET_NAME, SUBNET_NAME, args.resource_group, credential, args.key_vault, nsg_name)
    
    print("connection process completed!!\n")
    
    # for i in range(len(args.workload_paths)):
    #     config_and_run_tb(args.configs[i], args.workload_paths[i])
        
    print("config process completed!!\n")

    

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
    parser_deploy.add_argument("coonection", type=str, choices=connection_choices)
    parser_deploy.set_defaults(func=run_deployment)

    parser_deploy.add_argument('resource_group', type=str)
    parser_deploy.add_argument('location', type=str)
    parser_deploy.add_argument("--workload_paths", nargs="+")
    parser_deploy.add_argument("--workload_names", nargs="+")
    parser_deploy.add_argument('key_vault', type=str)
    parser_deploy.add_argument("--configs", nargs="+")
    parser_deploy.add_argument("--replica",type=int)
    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
        sys.exit(1)
    args.func(args)   
if __name__ == '__main__':
    deployer()


    #test

