import argparse
import sys


def run_deployment(args):
    pass

def deployer():
    parser = argparse.ArgumentParser(prog='deployer')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='Additional help')
    parser_deploy = subparsers.add_parser(
        'deploy', aliases=['d'], help='Deploy help')

    compute_choices = ['AKS', 'VMs']
    connection_choices = ["EventHubs", "TCP"]
    parser_deploy.add_argument("compute", type=str, choices=compute_choices)
    parser_deploy.add_argument("coonection", type=str, choices=connection_choices)
    parser_deploy.set_defaults(func=run_deployment)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
        sys.exit(1)
    
if __name__ == '__main__':
    deployer()
    