# gem5_examples
gem5 configs for me to reference later on


## Functioning
mult_drams.py   
mult_hbms.py     
simple_hbm.py   
simple_tgen.py(must be run with appropriate parameters)    
tgen_HBM.py(must be run with appropriate parameters)    


## Not Functioning   
TestBenchSystem.py    
FGDRAM.py(just a class)    



## Descriptions  

### mult_drams.py*    
This file has 2 DDR3 drams setup.    

### mult_hbms.py*    
This file has a variable number of HBM drams setup, change the "num_chnls" variable to change number of HBM channels.  

### simple_hbm.py*    
This file has a replaces the DDR3 channel with an HBM channel.

### simple_tgen.py*    
This file has a replaces the cpu with a linear traffic generator.

### tgen_HBM.py    
This file takes in command line arguments to change the number of HBM dram channels as well as the number of traffic generators


\* - (For simplicity this code is largely taken from gem5/configs/learning_gem5/part2/simple_memobj.py)
