#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: bquantump
# GNU Radio version: 3.9.1.0

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
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.source_port = source_port = 60001
        self.source_ip = source_ip = "20.94.254.69"
        self.sink_port = sink_port = 65001
        self.sink_ip = sink_ip = "10.0.0.6"

        ##################################################
        # Blocks
        ##################################################
        self.network_udp_sink_0 = network.udp_sink(gr.sizeof_gr_complex, 1, '127.0.0.1', sink_port, 0, 1472, False)
        self.azure_software_radio_difi_source_cpp_0_0 = azure_software_radio.difi_source_cpp_fc32(source_ip, source_port, 1, 0, int(8), int(0))



        ##################################################
        # Connections
        ##################################################
        self.connect((self.azure_software_radio_difi_source_cpp_0_0, 0), (self.network_udp_sink_0, 0))


    def get_source_port(self):
        return self.source_port

    def set_source_port(self, source_port):
        self.source_port = source_port

    def get_source_ip(self):
        return self.source_ip

    def set_source_ip(self, source_ip):
        self.source_ip = source_ip

    def get_sink_port(self):
        return self.sink_port

    def set_sink_port(self, sink_port):
        self.sink_port = sink_port

    def get_sink_ip(self):
        return self.sink_ip

    def set_sink_ip(self, sink_ip):
        self.sink_ip = sink_ip




def main(top_block_cls=difi_to_udp, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
