from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import network
import azure_software_radio
class difi_to_udp(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, 'Not titled yet', catch_exceptions=True)
        self.source_port = source_port = 60001
        self.source_ip = source_ip = '20.112.37.210'
        self.sink_port = sink_port = 65001
        self.sink_ip = sink_ip = '10.0.0.6'
        self.azure_software_radio_difi_source_cpp_0_0 = azure_software_radio.difi_source_cpp_fc32(source_ip, source_port, 1, 0, int(8), int(0))
        self.udp0 = network.udp_sink(gr.sizeof_gr_complex, 1, '10.0.0.4', sink_port, 0, 1472, False)
        self.connect((self.azure_software_radio_difi_source_cpp_0_0, 0), (self.udp0, 0))
