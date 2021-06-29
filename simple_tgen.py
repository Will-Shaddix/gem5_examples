# -*- coding: utf-8 -*-
# Copyright (c) 2017 Jason Lowe-Power
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" This file creates a barebones system and executes 'hello', a simple Hello
World application. Adds a simple memobj between the CPU and the membus.

This config file assumes that the x86 ISA was built.
"""

# import the m5 (gem5) library created when gem5 is built
import m5
# import all of the SimObjects
from m5.objects import *
from m5.util.convert import *


import argparse
import math

# Command line arguments
#
#   needed for linear traffic gen: duration, min_addr, max_addr, 
#   block_size, min_period, max_period, rd_perc
#

parser = argparse.ArgumentParser()

parser.add_argument('mem_type', type = str, default = "DDR",
help = '''memory model to simulate''')

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
print("duration: ", options.duration, "  max_addr: ", options.max_addr)

#
#
#





# create the system we are going to simulate
system = System()

# Set the clock fequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = 'timing'               # Use timing accesses
system.mem_ranges = [AddrRange('512MB')] # Create an address range

# Create a simple CPU
system.cpu = TimingSimpleCPU()

system.tgens = [PyTrafficGen() for i in range(1)]

# for i, tgen in enumerate(tgens):
#     tgen.port = system.membus.cpu_side_ports

print("tgens = ", system.tgens)

# tgen.createLinear(options.duration,
#                             options.min_addr,
#                             options.max_addr,
#                             options.block_size,
#                             options.min_period,
#                             options.max_period,
#                             options.rd_perc, 0)



#tgen.port = system.membuses[i].cpu_side_ports

# Create the simple memory object
system.memobj = SimpleMemobj()

# Hook the CPU ports up to the cache
system.cpu.icache_port = system.memobj.inst_port
system.cpu.dcache_port = system.memobj.data_port

# Create a memory bus, a coherent crossbar, in this case
system.membus = SystemXBar(width = 64, max_routing_table_size = 16777216)


for i, tgen in enumerate(system.tgens):
    tgen.port = system.membus.cpu_side_ports
    print("tgen.port = ", tgen.port)
    



# Connect the memobj
system.memobj.mem_side = system.membus.cpu_side_ports

# create the interrupt controller for the CPU and connect to the membus
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Create a DDR3 memory controller and connect it to the membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Create a process for a simple "Hello World" application
process = Process()
# Set the command
# grab the specific path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
binpath = os.path.join(thispath, '../../../',
                       'tests/test-progs/hello/bin/x86/linux/hello')
# cmd is a list which begins with the executable (like argv)
process.cmd = [binpath]
# Set the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.createThreads()

system.workload = SEWorkload.init_compatible(binpath)

# set up the root SimObject and start the simulation
root = Root(full_system = False, system = system)
# instantiate all of the objects we've created above
m5.instantiate()

if options.mode == 'linear':
    print("in linear")
    for i, tgen in enumerate(system.tgens):
        options.min_addr = i * 64
        tgen.start(tgen.createLinear(options.duration,
                            options.min_addr,
                            options.max_addr,
                            options.block_size,
                            options.min_period,
                            options.max_period,
                            options.rd_perc,
                            0))

print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))
