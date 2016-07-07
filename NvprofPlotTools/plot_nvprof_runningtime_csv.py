#! /usr/bin/python                                                              

import numpy as np
import matplotlib.pyplot as plt
import re                                                                       
import sys
import csv
import collections

if len(sys.argv) == 1:
  print "Input file name is empty"
  exit()

num_files = len(sys.argv) - 1

# Obtain all trace files if there are many
filename_list = []
for i in range(num_files):
  # Obtain file name
  filename_list.append(sys.argv[i+1])

# Regular expression to extract values
regex_data_transfer = re.compile(r"\[CUDA mem.*\]")
#regex_int = re.compile(r"^\(*(\d+)\)*$")
#regex_float = re.compile(r"(\d+\.\d+(e\+)*\d*)(?:\w+\/\w+|%)*")

# Trace layout
# col 1: Duration
# col 16: Process name

# Running time dictionary
runningtime_dict = collections.OrderedDict()

# Key for kernel execution duration
key_kernel = "kernel"

# Key for data transfer duration
key_data_transfer = "data_transfer"

# Extract occupancy of each trace file
for filename in filename_list:
  # Obtain csv object
  log_file = csv.reader(open(filename, "rb"))

  # Number of useless lines
  num_useless_lines = 4

  for i in range(num_useless_lines):
    next(log_file)

  unit_row = next(log_file)
  unit = unit_row[1]

  # Setup running time for two portions
  runningtime_kernel = 0.0
  runningtime_data_transfer = 0.0

  # Setup sub dictionary(Don't have to be an ordered one)
  runningtime_dict[filename] = {}

  # Collect for each file
  for row in log_file:
    if len(row) < 17:
      continue

    process_name = row[16]
    # Differentiate data transfer from normal kernel execution
    if regex_data_transfer.match(process_name):
      if unit == "ms":
        runningtime_data_transfer += float(row[1])
      elif unit == "us":
        runningtime_data_transfer += float(row[1]) / 1000
    else:
      if unit == "ms":
        runningtime_kernel += float(row[1])
      else:
        runningtime_kernel += float(row[1]) / 1000

  # Assign specific running time to dictionary
  runningtime_dict[filename][key_kernel] = runningtime_kernel
  runningtime_dict[filename][key_data_transfer] = runningtime_data_transfer

# General information
file_num = len(filename_list)
n_groups = file_num
bar_width = 0.35
opacity = 0.4
index = np.arange(0, n_groups)
prefix = "runningtime"

regex_batch_size = re.compile(r".*_(\d+)_.*")

# Set up color and label map
# Limitation for color map: at most 10 different input files
color_map = [None] * 10
color_map[0] = 'r'
color_map[1] = 'b'
color_map[2] = 'g'
color_map[3] = 'c'
color_map[4] = 'm'
color_map[5] = 'y'
color_map[6] = 'k'
color_map[7] = '0.25'
color_map[8] = '0.75'
color_map[9] = '0.50'

label_map = []
for filename in filename_list:
  label_map.append('Batch size: ' + regex_batch_size.match(filename).group(1))

# Collect data and generate plot
plt.figure(1)
fig, ax = plt.subplots()

kernel_runningtime_list = []
data_transfer_runningtime_list = []
for filename in runningtime_dict:
  kernel_runningtime_list.append(runningtime_dict[filename][key_kernel])
  data_transfer_runningtime_list.append(runningtime_dict[filename]\
                                        [key_data_transfer])

p1 = plt.bar(index, kernel_runningtime_list, bar_width,
             alpha=opacity,
             color=color_map[0])
p2 = plt.bar(index, data_transfer_runningtime_list, bar_width,
             alpha=opacity,
             color=color_map[1],
             bottom=kernel_runningtime_list)


plt.xlabel('Batch size')
plt.ylabel('Running time')

plt.xticks(index + bar_width/2, label_map, rotation='vertical')
#plt.legend(loc=2, ncol=2)
plt.legend((p1[0], p2[0]), ('Kernel', 'Data Transfer'), 
           bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=3, mode="expand", borderaxespad=0.)
           #ncol=2)
plt.tight_layout()
plt.savefig(prefix + '.png', bbox_inches='tight')


