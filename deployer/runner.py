import os
import yaml
import sys
from multiprocessing import Process


workload_file = sys.argv[1]
config_yml = sys.argv[2]

instance_name = os.path.split(workload_file)[-1]
instance_name = instance_name.split(".")[0]
workload_path = os.path.abspath(workload_file)
# open the file
f = open(workload_path, "r")
# read the entire file in as a string
str = f.read()
f.close()
# call exec on the on the string set abo
exec(str)


instance = locals()[instance_name]()


config_path = os.path.abspath(config_yml)

with open(config_path) as f:
    dict = yaml.load(f, Loader=yaml.FullLoader)


for key in dict.keys():
    setattr(instance, key, dict[key])
print(instance)
locals()['main'](instance)