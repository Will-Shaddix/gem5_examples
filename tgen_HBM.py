# import the m5 (gem5) library created when gem5 is built
import m5
# import all of the SimObjects
from m5.objects import *
from m5.util.convert import *

import argparse
import math


# Helper Functions
#

def createLinearTraffic(tgen, tgen_options):
    yield tgen.createLinear(tgen_options.duration,
                            tgen_options.min_addr,
                            tgen_options.max_addr,
                            tgen_options.block_size,
                            tgen_options.min_period,
                            tgen_options.max_period,
                            tgen_options.rd_perc, 0)
    yield tgen.createExit(0)


parser = argparse.ArgumentParser()

# parser.add_argument('mem_type', type = str, default = "HBM",
# help = '''memory model to simulate''')

parser.add_argument('num_chnls', type = int, default = 1,
                    help = 'number of channels in the memory system, \
                    could only be a power of 2, e.g. 1, 2, 4, 8, ..')

parser.add_argument('banks_per_channel', type = int, default = 32,
                    help = 'number of banks per LLM channel')
                    
parser.add_argument('unified_queue', type = int, default = False,
                    help = 'Unified queue at the MemScheduler')

parser.add_argument('wr_perc', type = int, default = 50,
                    help = '''Percentage of write request
                    to force servicing writes in MemScheduler''')

# parser.add_argument('paging_policy', type = str,
#                     help = '''paging policy''')

parser.add_argument('num_tgens', type = int, default = 1,
                    help = 'number of traffic generators to create \
                        synthetic traffic')

parser.add_argument('mode', type = str, default = "linear",
                    help = 'type of traffic to be generated')

parser.add_argument('duration', type = str, default = "1us",
                    help = '''real time duration to generate traffic
                    e.g. 1s, 1ms, 1us, 1ns''')

parser.add_argument('injection_rate', type = int, default = 1,
                    help = '''The amount of traffic generated
                    by the traffic generator in GBps''')

parser.add_argument('rd_perc', type = int, default = 50,
                    help = '''Percentage of read request,
                    rd_perc = 100 - write requests percentage''')

parser.add_argument('data_limit', type = int, default = 0)

options = parser.parse_args()

options.block_size = 64
options.duration = int(toLatency(options.duration) * 1e12)
options.min_addr = 0
options.max_addr = toMemorySize(str(512 * options.num_chnls) + 'MB')

injection_period = int((1e12 * options.block_size) /
                    (options.injection_rate * 1073741824))
options.min_period = injection_period
options.max_period = injection_period

print("all options: ", options, "\n")


# create the system we are going to simulate
system = System()

# Set the clock fequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')] # Create an address range
addr_range = system.mem_ranges[0]

system.tgens = [PyTrafficGen() for i in range(options.num_tgens)]

system.membus = SystemXBar(width = 64, max_routing_table_size = 16777216)


for i, tgen in enumerate(system.tgens):
    tgen.port = system.membus.cpu_side_ports
    print("tgen.port = ", tgen.port)


mem_ctrls = []

num_chnls = options.num_chnls
intlv_bits = int(math.log(num_chnls, 2))
cache_line_size = 64
intlv_low_bit = int(math.log(cache_line_size, 2))

for chnl in range(num_chnls):
            interface = HBM_1000_4H_1x128()
            interface.range = AddrRange(addr_range.start, size = addr_range.size(),
                        intlvHighBit = intlv_low_bit + intlv_bits - 1,
                        xorHighBit = 0,
                        intlvBits = intlv_bits,
                        intlvMatch = chnl)
            ctrl = MemCtrl()
            ctrl.dram = interface

            #ctrl.dram.null = True
            #ctrl.dram.addr_mapping = addr_map
            #ctrl.dram.page_policy = page_policy
            mem_ctrls.append(ctrl)

system.mem_ctrls = mem_ctrls

for mem_ctrl in system.mem_ctrls:
    mem_ctrl.port = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports



root = Root(full_system = False, system = system)
# instantiate all of the objects we've created above
m5.instantiate()

if options.mode == 'linear':
    #print("in linear")
    for i, tgen in enumerate(system.tgens):
        #print("tgen type = ", type(tgen))
        options.min_addr = i * 64

        # print("tgen type = ", type(tgen))
       
        # print("before tgen start")
        tgen.start(createLinearTraffic(tgen, options))
        # print("after tgen start")


print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))










