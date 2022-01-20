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
        self.source_ip = source_ip = '52.183.87.134'
        self.sink_port = sink_port = 65001
        self.sink_ip = sink_ip = '10.0.0.6'
        self.azure_software_radio_difi_source_cpp_0_0 = azure_software_radio.difi_source_cpp_fc32(source_ip, source_port, 1, 0, int(16), int(0))
        self.udp0 = network.udp_sink(gr.sizeof_gr_complex, 1, '10.0.0.4', sink_port, 0, 1472, False)
        self.udp1 = network.udp_sink(gr.sizeof_gr_complex, 1, '10.0.0.6', sink_port, 0, 1472, False)
        self.connect((self.azure_software_radio_difi_source_cpp_0_0, 0), (self.udp0, 0))
        self.connect((self.azure_software_radio_difi_source_cpp_0_0, 0), (self.udp1, 0))

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