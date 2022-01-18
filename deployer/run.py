import subprocess
import sys
workload_file = sys.argv[1]
config_yml = sys.argv[2]
cmd = f'python3 runner.py {workload_file} {config_yml}'
p = subprocess.Popen(cmd, start_new_session=True, shell=True)