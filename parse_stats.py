# This python file will read in a stats.txt file from gem5 and parse it based on the given stats
# The expected input is a path to the stats.txt, a file containing all the  stats you want, and an output directory to write this information for.
# This Should enable graph generation to be much easier

import argparse


args = argparse.ArgumentParser()

args.add_argument(
    "stats_path",
    type = str,
    help = "Path to stats.txt"
)

args.add_argument(
    "param",
    type = str,
    help = "Path to txt file wit parameters to read in"
)

args.add_argument(
    "output_dir",
    type = str,
    help = "Path to output directory"
)

options = args.parse_args()

print(options)

f = open(options.stats_path, 'r')

content = f.readlines()

param_f = open(options.param, 'r')
write_f = open(options.output_dir, 'a')

params = param_f.readlines()

write_f.write("\n" + options.stats_path + ":\n")

for line in content: # for each line in stats.txt
    split_line = line.split() # split the line by white space
    if len(split_line) > 1:# tests if this line of stats is actual stats
        for param in params:# for every parameter in param file
            if param.split()[0] in split_line[0]:# checks if param is in the stat line
                # print(split_line[0])
                write_f.write("\t" + split_line[0] + ": " + split_line[1]+ "\n")
        

param_f.close()
f.close()

