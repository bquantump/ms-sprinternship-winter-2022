import argparse
import sys

from azure.core import credentials
from deployer import create_all_vm, make_rg_if_does_not_exist
from azure.identity import DefaultAzureCredential
import os

from deployer.runner import config_and_run_tb

def run_deployment(args):
    VNET_NAME = "python-example-vnet"
    SUBNET_NAME = "python-example-subnet"
    IP_NAME = "python-example-ip"
    IP_CONFIG_NAME = "python-example-ip-config"
    NIC_NAME = "python-example-nic"
    credential = DefaultAzureCredential()
    subscription_id = os.environ["SUBSCRIPTION_ID"]

    if len(args.workload_names) != len(args.configs) and len(args.workloads_paths) != len(args.configs):
        raise RuntimeError('length of workloads does not match length of config')
    
        

    #make_rg_if_does_not_exist(subscription_id, args.resource_group, credential, args.location)
    #create_all_vm(args.workload_names, args.workload_paths,args.location, credential, args.resource_group, args.key_vault, 
     #               os.environ['OBJECT_ID'], VNET_NAME, SUBNET_NAME, IP_NAME, IP_CONFIG_NAME, NIC_NAME, subscription_id)
    for i in range(len(args.workload_paths)):
        config_and_run_tb(args.configs[i], args.workload_paths[i])

    

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

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
        sys.exit(1)
    args.func(args)   
if __name__ == '__main__':
    deployer()


    #test

