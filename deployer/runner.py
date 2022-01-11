import os
import yaml

def config_and_run_tb(config_yml, workload_file) :
    workload_path = os.path.abspath(workload_file)
    # open the file
    f = open(workload_path, "r")
    # read the entire file in as a string
    str = f.read()
    f.close()
    # call exec on the on the string set abo
    exec(str)
    

    instance = locals()['difi_to_udp']()
    

    config_path = os.path.abspath(config_yml)

    with open(config_path) as f:
        dict = yaml.load(f, Loader=yaml.FullLoader)
    

    instance.set_source_port(dict['source_port'])
    instance.set_source_ip(dict['source_ip'])
    instance.set_sink_port(dict['sink_port'])
    instance.set_sink_ip(dict['sink_ip'])

    print(instance.get_source_port())
    print(instance.get_source_ip())
    print(instance.get_sink_port())
    print(instance.get_sink_ip())
    

    locals()['main']()

if __name__ == '__main__':
    config_path = os.path.join('..', 'eng', 'sample_configs', 'test_one.yml')
    workload_path = os.path.join('..', 'eng', 'grc', 'test_file.py')
    config_and_run_tb(config_path, workload_path)