#! /usr/bin/python                                                              

import numpy as np
import matplotlib.pyplot as plt
import re                                                                       
import sys
import collections

if len(sys.argv) == 1:
  print "Input file name is empty"
  exit()
filename = sys.argv[len(sys.argv)-1]                                                              

fn = open(filename, 'r')                                                        

regex_kernel = re.compile(r".*Kernel:.*(?:void)? (?:\w+(?:::))*(\w+)(?:<.*>)*\(.*\)$")
regex_int = re.compile(r"^\(*(\d+)\)*$")
regex_float = re.compile(r"(\d+\.\d+(e\+)*\d*)(?:\w+\/\w+|%)*")

kernel_id = 0
kernel_name = ""
metric_flag = False
metric_name_idx = 1
metric_avg_value_idx = -1
metric_dict = collections.OrderedDict()
for content in fn.readlines():
  if regex_kernel.match(content):
    kernel_name = regex_kernel.match(content).group(1) + "_" + str(kernel_id)
    metric_flag = True
    kernel_id += 1
    metric_dict[kernel_name] = {}
    continue
  if metric_flag:
    line = content.split()
    if regex_int.match(line[metric_avg_value_idx]):
      value = int(regex_int.match(line[metric_avg_value_idx]).group(1))
    elif regex_float.match(line[metric_avg_value_idx]):
      value = float(regex_float.match(line[metric_avg_value_idx]).group(1))
    metric_dict[kernel_name][line[metric_name_idx]] = value

# General information
kernel_name_list = []
for key in metric_dict:
  kernel_name_list.append(key)
kernel_num = len(kernel_name_list)
n_groups = kernel_num
opacity = 0.4
index = np.arange(n_groups)
index_wider = np.arange(0, n_groups*1.8, 1.8)
regex_file = re.compile(r"(\w+).csv")
if regex_file.match(filename):
  prefix = regex_file.match(filename).group(1)

# Collect data and generate plot for IPC
ipc = []
issued_ipc = []
for kernel in kernel_name_list:
  ipc.append(metric_dict[kernel]["ipc"])
  issued_ipc.append(metric_dict[kernel]["issued_ipc"])
bar_width = 0.35
plt.figure(1)
fig, ax = plt.subplots()

rects1 = plt.bar(index, ipc, bar_width,
                 alpha=opacity,
                 color='b',
                 label='ipc')

rects2 = plt.bar(index + bar_width, issued_ipc, bar_width,
                 alpha=opacity,
                 color='r',
                 label='issued_ipc')

plt.xlabel('Kernels')
plt.ylabel('')

plt.xticks(index + bar_width, kernel_name_list, rotation='vertical')
plt.legend(loc=2)
plt.tight_layout()
plt.savefig(prefix + '_ipc.png')

# Collect data and generate plot for occupancy
occupancy = []
for kernel in kernel_name_list:
  occupancy.append(metric_dict[kernel]["achieved_occupancy"])
bar_width = 0.5
plt.figure(2)
fig, ax = plt.subplots()

rects1 = plt.bar(index, occupancy, bar_width,
                 alpha=opacity,
                 color='b',
                 label='achieved_occupancy')

plt.xlabel('Kernels')
plt.ylabel('')
plt.ylim((0, 1))

plt.xticks(index + bar_width/2, kernel_name_list, rotation='vertical')
plt.legend(loc=1)
plt.tight_layout()
plt.savefig(prefix + '_occupancy.png')

# Collect data and generate plot for utilization
l1_shared_utilization = []
l2_utilization = []
tex_utilization = []
dram_utilization = []
sysmem_utilization = []
ldst_fu_utilization = []
alu_fu_utilization = []
cf_fu_utilization = []
tex_fu_utilization = []
for kernel in kernel_name_list:
  l1_shared_utilization.append(metric_dict[kernel]["l1_shared_utilization"])
  l2_utilization.append(metric_dict[kernel]["l2_utilization"])
  tex_utilization.append(metric_dict[kernel]["tex_utilization"])
  dram_utilization.append(metric_dict[kernel]["dram_utilization"])
  sysmem_utilization.append(metric_dict[kernel]["sysmem_utilization"])
  ldst_fu_utilization.append(metric_dict[kernel]["ldst_fu_utilization"])
  alu_fu_utilization.append(metric_dict[kernel]["alu_fu_utilization"])
  cf_fu_utilization.append(metric_dict[kernel]["cf_fu_utilization"])
  tex_fu_utilization.append(metric_dict[kernel]["tex_fu_utilization"])
bar_width = 0.15
plt.figure(3)
fig, ax = plt.subplots(figsize=(20,10))

rects1 = plt.bar(index_wider, l1_shared_utilization, bar_width,
                 alpha=opacity,
                 color='b',
                 label='l1_shared_utilization')
rects2 = plt.bar(index_wider+bar_width, l2_utilization, bar_width,
                 alpha=opacity,
                 color='r',
                 label='l2_utilization')
rects3 = plt.bar(index_wider+2*bar_width, tex_utilization, bar_width,
                 alpha=opacity,
                 color='g',
                 label='tex_utilization')
rects4 = plt.bar(index_wider+3*bar_width, dram_utilization, bar_width,
                 alpha=opacity,
                 color='c',
                 label='dram_utilization')
rects5 = plt.bar(index_wider+4*bar_width, sysmem_utilization, bar_width,
                 alpha=opacity,
                 color='m',
                 label='sysmem_utilization')
rects6 = plt.bar(index_wider+5*bar_width, ldst_fu_utilization, bar_width,
                 alpha=opacity,
                 color='y',
                 label='ldst_fu_utilization')
rects7 = plt.bar(index_wider+6*bar_width, alu_fu_utilization, bar_width,
                 alpha=opacity,
                 color='k',
                 label='alu_fu_utilization')
rects8 = plt.bar(index_wider+7*bar_width, cf_fu_utilization, bar_width,
                 alpha=opacity,
                 color='0.25',
                 label='cf_fu_utilization')
rects9 = plt.bar(index_wider+8*bar_width, tex_fu_utilization, bar_width,
                 alpha=opacity,
                 color='0.75',
                 label='tex_fu_utilization')

plt.xlabel('Kernels')
plt.ylabel('')
plt.ylim((0, 10))

plt.xticks(index_wider + (bar_width*9)/2, kernel_name_list, rotation='vertical')
plt.legend(loc=9, ncol=3)
plt.tight_layout()
plt.savefig(prefix + '_utlization.png')

# Collect data and generate plot for stall reason
stall_inst_fetch = []
stall_exec_dependency = []
stall_texture = []
stall_sync = []
stall_other = []
stall_memory_dependency = []
stall_pipe_busy = []
stall_constant_memory_dependency = []
stall_memory_throttle = []
stall_not_selected = []
for kernel in kernel_name_list:
  stall_inst_fetch.append(metric_dict[kernel]["stall_inst_fetch"])
  stall_exec_dependency.append(metric_dict[kernel]["stall_exec_dependency"])
  stall_texture.append(metric_dict[kernel]["stall_texture"])
  stall_sync.append(metric_dict[kernel]["stall_sync"])
  stall_other.append(metric_dict[kernel]["stall_other"])
  stall_memory_dependency.append(metric_dict[kernel]["stall_memory_dependency"])
  stall_pipe_busy.append(metric_dict[kernel]["stall_pipe_busy"])
  stall_constant_memory_dependency.append(metric_dict[kernel]["stall_constant_memory_dependency"])
  stall_memory_throttle.append(metric_dict[kernel]["stall_memory_throttle"])
  stall_not_selected.append(metric_dict[kernel]["stall_not_selected"])
bar_width = 0.15
plt.figure(4)
fig, ax = plt.subplots(figsize=(20,10))

rects1 = plt.bar(index_wider, stall_inst_fetch, bar_width,
                 alpha=opacity,
                 color='b',
                 label='stall_inst_fetch')
rects2 = plt.bar(index_wider+bar_width, stall_exec_dependency, bar_width,
                 alpha=opacity,
                 color='r',
                 label='stall_exec_dependency')
rects3 = plt.bar(index_wider+2*bar_width, stall_texture, bar_width,
                 alpha=opacity,
                 color='g',
                 label='stall_texture')
rects4 = plt.bar(index_wider+3*bar_width, stall_sync, bar_width,
                 alpha=opacity,
                 color='c',
                 label='stall_sync')
rects5 = plt.bar(index_wider+4*bar_width, stall_other, bar_width,
                 alpha=opacity,
                 color='m',
                 label='stall_other')
rects6 = plt.bar(index_wider+5*bar_width, stall_memory_dependency, bar_width,
                 alpha=opacity,
                 color='y',
                 label='stall_memory_dependency')
rects7 = plt.bar(index_wider+6*bar_width, stall_pipe_busy, bar_width,
                 alpha=opacity,
                 color='k',
                 hatch='/',
                 label='stall_pipe_busy')
rects8 = plt.bar(index_wider+7*bar_width, stall_constant_memory_dependency, bar_width,
                 alpha=opacity,
                 color='0.25',
                 hatch='//',
                 label='stall_constant_memory_dependency')
rects9 = plt.bar(index_wider+8*bar_width, stall_memory_throttle, bar_width,
                 alpha=opacity,
                 color='0.5',
                 hatch='-',
                 label='stall_memory_throttle')
rects9 = plt.bar(index_wider+9*bar_width, stall_not_selected, bar_width,
                 alpha=opacity,
                 color='0.75',
                 hatch='o',
                 label='stall_not_selected')

plt.xlabel('Kernels')
plt.ylabel('')
plt.ylim((0, 100))

plt.xticks(index_wider + (bar_width*10)/2, kernel_name_list, rotation='vertical')
plt.legend(loc=9, ncol=4)
plt.tight_layout()
plt.savefig(prefix + '_stall_reason.png')

# Collect data and generate plot for eligible warps per cycle
eligible_warps_per_cycle = []
for kernel in kernel_name_list:
  eligible_warps_per_cycle.append(metric_dict[kernel]["eligible_warps_per_cycle"])
bar_width = 0.5
plt.figure(5)
fig, ax = plt.subplots()

rects1 = plt.bar(index, eligible_warps_per_cycle, bar_width,
                 alpha=opacity,
                 color='b',
                 label='eligible_warps_per_cycle')

plt.xlabel('Kernels')
plt.ylabel('')

plt.xticks(index + bar_width/2, kernel_name_list, rotation='vertical')
plt.legend(loc=2)
plt.tight_layout()
plt.savefig(prefix + '_eligible_warp.png')

#for key in metric_dict:
#  print key
#print len(metric_dict)
#print metric_dict

