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
        _ = resource_client.resource_groups.create_or_update(rg_name, {
            'location': location
        }
        )

def make_difi_to_udp(forwarding_private_ips, public_ip):
    base_string = "from gnuradio import gr\n" \
    "from gnuradio.filter import firdes\n" \
    "from gnuradio.fft import window\n" \
    "import sys\n" \
    "import signal\n" \
    "from argparse import ArgumentParser\n" \
    "from gnuradio.eng_arg import eng_float, intx\n" \
    "from gnuradio import eng_notation\n" \
    "from gnuradio import network\n" \
    "import azure_software_radio\n" \
    "class difi_to_udp(gr.top_block):\n" \
    "    def __init__(self):\n" \
    "        gr.top_block.__init__(self, 'Not titled yet', catch_exceptions=True)\n" \
    "        self.source_port = source_port = 60001\n" \
    f"        self.source_ip = source_ip = '{public_ip}'\n" \
    "        self.sink_port = sink_port = 65001\n" \
    "        self.sink_ip = sink_ip = '10.0.0.6'\n" \
    "        self.azure_software_radio_difi_source_cpp_0_0 = azure_software_radio.difi_source_cpp_fc32(source_ip, source_port, 1, 0, int(8), int(0))\n"
    for k, i in enumerate(forwarding_private_ips):
        base_string += f"        self.udp{k} = network.udp_sink(gr.sizeof_gr_complex, 1, '{i}', sink_port, 0, 1472, False)\n"
    for k, _ in enumerate(forwarding_private_ips):
        base_string += f"        self.connect((self.azure_software_radio_difi_source_cpp_0_0, 0), (self.udp{k}, 0))\n"
    print(base_string)
    with open("difi_to_udp.py", "w+") as file:
        file.write(base_string)
        