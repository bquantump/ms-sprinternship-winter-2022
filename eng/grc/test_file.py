#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: bquantump
# GNU Radio version: 3.9.1.0

import sys
import signal
from argparse import ArgumentParser




class test_file:

    def __init__(self):

        ##################################################
        # Variables
        ##################################################
        self.source_port = source_port = 60001
        self.source_ip = source_ip = "20.94.254.69"
        self.sink_port = sink_port = 65001
        self.sink_ip = sink_ip = "10.0.0.6"


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




def main(top_block_cls=test_file, options=None):
    tb = top_block_cls()
    print("we ran the main function...")
