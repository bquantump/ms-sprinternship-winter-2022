#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: bquantump
# GNU Radio version: 3.9.1.0

from gnuradio import analog
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




class workload2(gr.top_block):

    def __init__(self):
        from gnuradio import analog
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

        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000
        self.rec_port = rec_port = 60002
        self.freq = freq = "Endpoint=sb://hackathon2021.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=9IusLL3aVlo/DCHH/cI9Vkt+IF6PxnT/RByAXfRO6oM="
        self.conn_string = conn_string = "Endpoint=sb://hackathon2021.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=9IusLL3aVlo/DCHH/cI9Vkt+IF6PxnT/RByAXfRO6oM="

        ##################################################
        # Blocks
        ##################################################
        self.network_udp_source_0 = network.udp_source(gr.sizeof_gr_complex, 1, rec_port, 0, 1472, False, False, False)
        self.blocks_threshold_ff_0 = blocks.threshold_ff(.05, .25, 0)
        self.blocks_tagged_stream_to_pdu_0 = blocks.tagged_stream_to_pdu(blocks.float_t, 'packet_len')
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_float, 1, 12, "packet_len")
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_ff(2, 1)
        self.blocks_msg_meta_to_pair_0 = blocks.meta_to_pair('squelch_sob','detection!')
        self.blocks_complex_to_mag_0_0 = blocks.complex_to_mag(1)
        self.azure_software_radio_eventhub_sink_0 = azure_software_radio.EventHubSink('connection_string', conn_string, '', '', 'detect', '')
        self.analog_pwr_squelch_xx_0 = analog.pwr_squelch_ff(2.0, 1, 0, True)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_msg_meta_to_pair_0, 'outpair'), (self.azure_software_radio_eventhub_sink_0, 'in'))
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0, 'pdus'), (self.blocks_msg_meta_to_pair_0, 'inmeta'))
        self.connect((self.analog_pwr_squelch_xx_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_complex_to_mag_0_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.analog_pwr_squelch_xx_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_tagged_stream_to_pdu_0, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.blocks_multiply_const_xx_0, 0))
        self.connect((self.network_udp_source_0, 0), (self.blocks_complex_to_mag_0_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_rec_port(self):
        return self.rec_port

    def set_rec_port(self, rec_port):
        self.rec_port = rec_port

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq

    def get_conn_string(self):
        return self.conn_string

    def set_conn_string(self, conn_string):
        self.conn_string = conn_string




def main(tb, options=None):
    from gnuradio import analog
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
