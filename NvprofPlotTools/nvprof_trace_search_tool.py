#! /usr/bin/env python

import glob, os
import csv
import re
import sys
import collections
from optparse import OptionParser

metrics_trace_list = []
gpu_trace_list = []

regex_kernel = re.compile(r"(?:void)?\s?(?:\w+(?:::))*(\w+)(?:<.*>)*\(?.*\)?$")
regex_int = re.compile(r"^(?:\w+)*\s*\(*(\d+)\)*$")
regex_float = re.compile(r"(\d+\.\d+(e\+)*\d*)(?:\w+\/\w+|%)*")

kernel_idx = 1
metric_name_idx = 3
metric_avg_value_idx = 7;

def ObtainTraceFiles():
  current_dir = os.getcwd()
  os.chdir(current_dir)
  for f in glob.glob("*_metrics.csv"):
      metrics_trace_list.append(f)
  for f in glob.glob("*_gpu_trace.csv"):
      gpu_trace_list.append(f)

  if len(metrics_trace_list) == 0:
    print "No Metric trace file in current directory"
    exit()
  if len(gpu_trace_list) == 0:
    print "No GPU trace file in current directory"
    exit() 

trace_dict = collections.OrderedDict()
def GenerateDict():
  # Number of useless lines
  num_useless_lines = 6
  for f in metrics_trace_list:
    print "Process metric trace file: ", f
    reader = csv.reader(open(f, 'rb'))

    # The metric files has to be like <layer_name>_config_<batch_size>.csv
    layer_name = f[0:-4].split('_')[0]
    batch_size = int(f[0:-4].split('_')[2])
    print "  Layer name: ", layer_name
    print "  Batch size: ", str(batch_size)

    if layer_name not in trace_dict:
      trace_dict[layer_name] = collections.OrderedDict()

    if batch_size not in trace_dict[layer_name]:
      trace_dict[layer_name][batch_size] = collections.OrderedDict()

    for i in range(num_useless_lines):
      next(reader)
    for row in reader:
      # Get rid of other useless lines
      if len(row) < 8:
        continue
      if regex_kernel.match(row[kernel_idx]):
        content = row[kernel_idx]
        kernel_name = regex_kernel.match(content).group(1)
        if kernel_name not in trace_dict[layer_name][batch_size]:
          trace_dict[layer_name][batch_size][kernel_name] = collections.OrderedDict()
        # Obtain the metric value
        if regex_int.match(row[metric_avg_value_idx]):
          content = row[metric_avg_value_idx]
          value = int(regex_int.match(content).group(1))
        elif regex_float.match(row[metric_avg_value_idx]):
          content = row[metric_avg_value_idx]
          value = float(regex_float.match(content).group(1))
        metric_name = row[metric_name_idx]
        trace_dict[layer_name][batch_size][kernel_name][metric_name] = value

usage = "usage: %prog [option1] arg1,arg2 [option2] arg1,arg2"
def main():
  if len(sys.argv) == 1:
    print usage
    exit()

  parser = OptionParser(usage)
  parser.add_option("-l", "--layer", type="string", dest="layername",
                    help="Layer names seperated by coma", metavar="LAYER")
  parser.add_option("-n", "--batch-size", type="string", dest="batchsize",
                    help="Batch size seperated by coma", metavar="BATCH_SIZE")
  parser.add_option("-k", "--kernels", type="string", dest="kernels",
                    help="Kernels name seperated by coma", metavar="KERNELS")
  parser.add_option("-m", "--metrics", type="string", dest="metrics",
                    help="Metrics name seperated by coma", metavar="METRICS")

  (options, args) = parser.parse_args()
  if len(args) > 0:
    print "Arguments parsing fail. Possible reason: space occurred between arguments"
    exit()

  layer_list = []
  batchsize_list = []
  kernels_list = []
  metrics_list = []
  if options.layername != None:
    layer_list = options.layername.split(",")
  if options.batchsize != None:
    batchsize_list = options.batchsize.split(",")
  if options.kernels != None:
    kernels_list = options.kernels.split(",")
  if options.metrics != None:
    metrics_list = options.metrics.split(",")

  ObtainTraceFiles()
  
  GenerateDict()
  if len(trace_dict) == 0:
    print "NO trace found!!!"
    exit()

  for layer in layer_list:
    if layer not in trace_dict:
      print "Layer name INVALID!!!"
      exit()
    print "In layer: ", layer
    for batchsize in batchsize_list:
      batch_size = int(batchsize)
      if batch_size not in trace_dict[layer]:
        print " Batch size INVALID!!!"
        exit()
      print "For batch size: ", batch_size
      if len(kernels_list) == 0:
        kernels_list = trace_dict[layer][batch_size]
      for kernel in kernels_list:
        if kernel not in trace_dict[layer][batch_size]:
          print "Kernel name INVALID!!!"
          exit()
        print "   In Kernel: ", kernel
        for metric in metrics_list:
          if metric not in trace_dict[layer][batch_size][kernel]:
            print "Metric name: ", metric, " INVALID!!!"
            exit()
          print "     Metric: ", metric," ",  trace_dict[layer][batch_size][kernel][metric]


if __name__ == '__main__':
  main()
