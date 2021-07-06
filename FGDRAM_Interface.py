
# Values are from "Fine-Grained DRAM: Energy Efficient DRAM for
# Extreme Bandwidth Systems".
# channels/die(4-die stack): 128(512)
#  banks/channel: 2 pseudobanks
#  grains/bank: 4  (How to implement this?)
#  row-size/activate: 256B
# 
# 
# 
# 
# Wll use 128 channels/die 512 channels total

class FGDRAM(DRAMInterface):

    device_bus_width = 32
    device_rowbuffer_size = "256B"

    devices_per_rank = 1
    
    ranks_per_channel = 1  #just a guess for now


    #bank groups per rank possibly used for grains?



    # if banks per rank represents the pseudobanks 
    # than ranks per channel is the grains?
    # each grain gets its own channel

    # 2 pseudobanks
    banks_per_rank = 2

    tBurst = '16ns'

    tRCD = '16ns'

    tCL = '16ns'

    tRP = '16ns'

    tRAS = '29ns'

    tWR = '16ns'

    #tRTP = ?

    tCCD_L = '16ns'

    #tRFC = ?

    #tREFI = ?

    #tPPD = ?

    tRRD = '2ns'

    #tXAW = ?

    #activation_limit = ?

    #tXP = ?






