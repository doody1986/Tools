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
regex_kernel = re.compile(r"^(?:void)? (?:\w+(?:::))*(\w+)(?:<.*>)*\(.*\)$")
regex_int = re.compile(r"^\(*(\d+)\)*$")
regex_float = re.compile(r"(\d+\.\d+(e\+)*\d*)(?:\w+\/\w+|%)*")

# Trace layout
# col 0: Device
# col 1: Kernel name
# col 2: Number of invocation
# col 3: Metric name
# col 4: Metric description
# col 5: Min value
# col 6: Max value
# col 7: Avg value

# Key word metric
key_metric = "achieved_occupancy"

# Occupancy dictionary
occupancy_dict = collections.OrderedDict()

# Extract occupancy of each trace file
for filename in filename_list:
  # Obtain csv object
  log_file = csv.reader(open(filename, "rb"))

  # Number of useless lines
  num_useless_lines = 5

  for i in range(num_useless_lines):
    next(log_file)

  # Will not use`
  log_header = next(log_file)

  # Create dictionary for each file
  occupancy_dict[filename] = collections.OrderedDict()
  occupancy_kernel_dict = occupancy_dict[filename]
  kernel_id = 0
  kernel_list = []
  for row in log_file:
    kernel_name = row[1]

    # Insert kernel name if new kernel is encountered
    if kernel_name not in kernel_list:
      kernel_list.append(kernel_name) 
      kernel_id += 1
    
    # Obtain metric value according to the corresponding key metric
    if row[3] == key_metric:
      if regex_int.match(row[7]):
        value = int(regex_int.match(row[7]).group(1))
      elif regex_float.match(row[7]):
        value = float(regex_float.match(row[7]).group(1))
      # Obtain raw kernel name
      raw_kernel_name = kernel_list[kernel_id-1]
      if regex_kernel.match(raw_kernel_name):
        kernel_name_key = regex_kernel.match(raw_kernel_name).group(1) \
                          + "_" + str(kernel_id)
      occupancy_kernel_dict[kernel_name_key] = value

# General information
file_num = len(filename_list)
kernel_num = len(occupancy_dict[filename_list[0]])
kernel_name_list = []
for kernel in occupancy_dict[filename_list[0]]:
  kernel_name_list.append(kernel)
n_groups = kernel_num
bar_width = 0.35
opacity = 0.4
index = np.arange(0, n_groups*2.5, 2.5)
prefix = "occupancy"

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

idx = 0
for filename in occupancy_dict:
  occupancy = []
  for kernel in occupancy_dict[filename]:
    occupancy.append(occupancy_dict[filename][kernel])
  plt.bar(index+idx*bar_width, occupancy, bar_width,
          alpha=opacity,
          color=color_map[idx],
          label=label_map[idx])
  idx += 1

plt.xlabel('Kernels')
plt.ylabel('')
#plt.ylim(0, 1.5)

plt.xticks(index + (bar_width*file_num)/2, kernel_name_list, rotation='vertical')
#plt.legend(loc=2, ncol=2)
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=3, mode="expand", borderaxespad=0.)
           #ncol=2)
plt.tight_layout()
plt.savefig(prefix + '.png', bbox_inches='tight')


