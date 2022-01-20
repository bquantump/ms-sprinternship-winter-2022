#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: bquantump
# GNU Radio version: 3.9.1.0

from gnuradio import blocks
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
import dspcore
import eventhubs
import numpy as np




class detect_workload(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.threshold = threshold = 24
        self.samp_rate = samp_rate = 32000
        self.conn_string = conn_string = "Endpoint=sb://hackathon2021.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=9IusLL3aVlo/DCHH/cI9Vkt+IF6PxnT/RByAXfRO6oM="
        self.chan_idx = chan_idx = 0
        self.ZC_ROOT = ZC_ROOT = 25
        self.rec_port = 60005

    def make_blocks_and_connect(self):
        ##################################################
        # Blocks
        ##################################################
        self.network_udp_source_0 = network.udp_source(gr.sizeof_gr_complex, 1, self.rec_port, 0, 1472, False, False, False)
        self.eventhubs_zc_detector_0 = eventhubs.zc_detector(self.ZC_ROOT,self.chan_idx,self.threshold)
        self.blocks_message_debug_0 = blocks.message_debug(True)
        self.azure_software_radio_eventhub_sink_0 = azure_software_radio.EventHubSink('connection_string', self.conn_string, '', '', 'detect', '')



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.eventhubs_zc_detector_0, 'detections'), (self.azure_software_radio_eventhub_sink_0, 'in'))
        self.msg_connect((self.eventhubs_zc_detector_0, 'detections'), (self.blocks_message_debug_0, 'print'))
        self.connect((self.network_udp_source_0, 0), (self.eventhubs_zc_detector_0, 0))


    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_conn_string(self):
        return self.conn_string

    def set_conn_string(self, conn_string):
        self.conn_string = conn_string

    def get_chan_idx(self):
        return self.chan_idx

    def set_chan_idx(self, chan_idx):
        self.chan_idx = chan_idx

    def get_ZC_ROOT(self):
        return self.ZC_ROOT

    def set_ZC_ROOT(self, ZC_ROOT):
        self.ZC_ROOT = ZC_ROOT




def main(tb):
    tb.make_blocks_and_connect()

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