#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Top Block
# GNU Radio version: 3.8.1.0

from gnuradio import analog
import math
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time
from datetime import datetime

class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.channel_spacing = channel_spacing = 500000
        self.width = width = 40000
        self.tuner = tuner = 868.95e6
        self.squelch = squelch = -25
        self.samp_rate = samp_rate = 1.024e6
        self.freq_offset = freq_offset = (channel_spacing / 2) + (channel_spacing * .1)
        self.demodgain = demodgain = 4
        self.cutoff = cutoff = 200000

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_source_0_1 = osmosdr.source(
            args="numchan=" + str(1) + " " + ''
        )
        self.osmosdr_source_0_1.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0_1.set_sample_rate(samp_rate)
        self.osmosdr_source_0_1.set_center_freq(tuner+freq_offset, 0)
        self.osmosdr_source_0_1.set_freq_corr(21, 0)
        self.osmosdr_source_0_1.set_gain_mode(False, 0)
        self.osmosdr_source_0_1.set_gain(10, 0)
        self.osmosdr_source_0_1.set_if_gain(24, 0)
        self.osmosdr_source_0_1.set_bb_gain(20, 0)
        self.osmosdr_source_0_1.set_antenna('', 0)
        self.osmosdr_source_0_1.set_bandwidth(0, 0)
        self.freq_xlating_fir_filter_xxx_0_1 = filter.freq_xlating_fir_filter_ccc(1, firdes.low_pass(1, samp_rate,cutoff, width,  firdes.WIN_BLACKMAN, 6.76), -freq_offset, samp_rate)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, 'capture_' + datetime.today().strftime('%Y%m%d%H%M%S'), False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.analog_simple_squelch_cc_0 = analog.simple_squelch_cc(squelch, 1)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(demodgain)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.analog_simple_squelch_cc_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0_1, 0), (self.analog_simple_squelch_cc_0, 0))
        self.connect((self.osmosdr_source_0_1, 0), (self.freq_xlating_fir_filter_xxx_0_1, 0))


    def get_channel_spacing(self):
        return self.channel_spacing

    def set_channel_spacing(self, channel_spacing):
        self.channel_spacing = channel_spacing
        self.set_freq_offset((self.channel_spacing / 2) + (self.channel_spacing * .1))

    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width
        self.freq_xlating_fir_filter_xxx_0_1.set_taps(firdes.low_pass(1, self.samp_rate,self.cutoff, self.width,  firdes.WIN_BLACKMAN, 6.76))

    def get_tuner(self):
        return self.tuner

    def set_tuner(self, tuner):
        self.tuner = tuner
        self.osmosdr_source_0_1.set_center_freq(self.tuner+self.freq_offset, 0)

    def get_squelch(self):
        return self.squelch

    def set_squelch(self, squelch):
        self.squelch = squelch
        self.analog_simple_squelch_cc_0.set_threshold(self.squelch)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.freq_xlating_fir_filter_xxx_0_1.set_taps(firdes.low_pass(1, self.samp_rate,self.cutoff, self.width,  firdes.WIN_BLACKMAN, 6.76))
        self.osmosdr_source_0_1.set_sample_rate(self.samp_rate)

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.freq_xlating_fir_filter_xxx_0_1.set_center_freq(-self.freq_offset)
        self.osmosdr_source_0_1.set_center_freq(self.tuner+self.freq_offset, 0)

    def get_demodgain(self):
        return self.demodgain

    def set_demodgain(self, demodgain):
        self.demodgain = demodgain
        self.analog_quadrature_demod_cf_0.set_gain(self.demodgain)

    def get_cutoff(self):
        return self.cutoff

    def set_cutoff(self, cutoff):
        self.cutoff = cutoff
        self.freq_xlating_fir_filter_xxx_0_1.set_taps(firdes.low_pass(1, self.samp_rate,self.cutoff, self.width,  firdes.WIN_BLACKMAN, 6.76))





def main(top_block_cls=top_block, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print("Error: failed to enable real-time scheduling.")
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
