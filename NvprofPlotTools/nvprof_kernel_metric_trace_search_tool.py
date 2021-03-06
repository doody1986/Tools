#! /usr/bin/env python

import glob, os
import csv
import re
import sys
import collections
from optparse import OptionParser
import sqlite3
import numpy as np
import matplotlib.pyplot as plt

metrics_trace_list = []

regex_kernel = re.compile(r"(?:void)?\s?(?:\w+(?:::))*(\w+)(<[^\(]+>)?\(?.*\)?")
regex_int = re.compile(r"^(?:[a-zA-z]+)*\s*\(*(\d+)\)*$")
regex_float = re.compile(r"(\d+\.\d+(e\+)*\d*)(?:\w+\/\w+|%)*")

kernel_idx = 1
metric_name_idx = 3
metric_avg_value_idx = 7

def ObtainMetricTraceFiles():
  current_dir = os.getcwd()
  os.chdir(current_dir)
  for f in glob.glob("*-metrics.csv"):
      metrics_trace_list.append(f)

  if len(metrics_trace_list) == 0:
    print "No Metric trace file in current directory"
    exit()

metric_trace_dict = collections.OrderedDict()
def GenerateMetricDict():
  # Number of useless lines
  num_useless_lines = 6
  for f in metrics_trace_list:
    print "Process metric trace file: ", f
    reader = csv.reader(open(f, 'rb'))

    # The metric files has to be like <propagation>_<layer_name>_config_<batch_size>.csv
    kernel_name = f[0:-4].split('-')[0]

      
    batch_size = f[0:-4].split('-')[1]
    invocation_order = f[0:-4].split('-')[2]
    print "  Kernel name:  ", kernel_name 
    print "  Batch size: ", batch_size
    print "  Invocation order: ", invocation_order
    if batch_size not in metric_trace_dict:
      metric_trace_dict[batch_size] = collections.OrderedDict()
    # Query the database
    conn = sqlite3.connect('../dnn_kernel.db')
    table_name = 'kernel_dict'
    c = conn.cursor()

    for i in range(num_useless_lines):
      next(reader)
    for row in reader:
      # Get rid of other useless lines
      if len(row) < 8:
        continue
      if regex_kernel.match(row[kernel_idx]):
        content = row[kernel_idx]
        kernel_name_from_trace = regex_kernel.match(content).group(1)
        template_arg_from_trace = regex_kernel.match(content).group(2) if\
          regex_kernel.match(content).group(2) != None else ""

      # Check the consistency of kernel name
      if kernel_name != kernel_name_from_trace:
        print kernel_name, kernel_name_from_trace
        print "Kernel name not consistent!!!"
        exit()
      full_name = kernel_name + template_arg_from_trace
      query_layer_name_str = "SELECT layername FROM "+table_name+" WHERE batchsize = "+batch_size+" AND fullname = '"+full_name+"' AND invocationorder = "+invocation_order
      c.execute(query_layer_name_str)
      layer_name_from_sql = c.fetchall()
      if len(layer_name_from_sql) > 1 or len(layer_name_from_sql) == 0:
        if kernel_name != 'dgrad_alg1_engine':
          print "Illegal layers!!!"
          print layer_name_from_sql
          exit()
        else:
          continue
      layer_name = layer_name_from_sql[0][0].encode("utf-8")

      query_propagation_str = "SELECT propagation FROM "+table_name+" WHERE batchsize = "+batch_size+" AND fullname = '"+full_name+"' AND invocationorder = "+invocation_order
      c.execute(query_propagation_str)
      propagation_from_sql = c.fetchall()
      if len(propagation_from_sql) > 1 or len(propagation_from_sql) == 0:
        if kernel_name != 'dgrad_alg1_engine':
          print "Ilegal propagation!!!"
          print propagation_from_sql
          exit()
        else:
          continue
      propagation = propagation_from_sql[0][0].encode("utf-8")

      if layer_name not in metric_trace_dict[batch_size]:
        metric_trace_dict[batch_size][layer_name] = collections.OrderedDict()
      if propagation not in metric_trace_dict[batch_size][layer_name]:
        metric_trace_dict[batch_size][layer_name][propagation] = collections.OrderedDict()

      if kernel_name not in metric_trace_dict[batch_size][layer_name][propagation]:
        metric_trace_dict[batch_size][layer_name][propagation][kernel_name] = collections.OrderedDict()
      # Obtain the metric value
      if regex_int.match(row[metric_avg_value_idx]):
        content = row[metric_avg_value_idx]
        value = int(regex_int.match(content).group(1))
      elif regex_float.match(row[metric_avg_value_idx]):
        content = row[metric_avg_value_idx]
        value = float(regex_float.match(content).group(1))
      metric_name = row[metric_name_idx]
      metric_trace_dict[batch_size][layer_name][propagation][kernel_name][metric_name] = value


def PlotByLayerName(title, layer_list, batch_size, metrics_list):
  metrics_dict = collections.OrderedDict()
  for layer in layer_list:
    for propagation in ["Forward", "Backward"]:
      for kernel in metric_trace_dict[batch_size][layer][propagation]:
        if kernel not in metrics_dict:
          metrics_dict[kernel] = collections.OrderedDict()
        l1_hit_rate = 0.0
        new_key = ""
        for metric in metrics_list:
          if title == "CacheHitRate":
            new_key = "l1_hit_rate"
            if new_key not in metrics_dict[kernel]:
              metrics_dict[kernel][new_key] = []
            if metric == "l1_cache_global_hit_rate" or metric == "l1_cache_local_hit_rate":
              l1_hit_rate += metric_trace_dict[batch_size][layer][propagation][kernel][metric]
              continue
          key = metric
          if key not in metrics_dict[kernel]:
            metrics_dict[kernel][key] = []
          value = metric_trace_dict[batch_size][layer][propagation][kernel][metric]
          metrics_dict[kernel][key].append(value)
        if title == "CacheHitRate":
          metrics_dict[kernel][new_key].append(l1_hit_rate)
  #print metrics_dict

  if title == "":
    exit()
  # Plot parameter
  opacity = 1.0
  bar_width = 0.35
  color_map = ['r', 'c', 'y', 'g', 'grey', 'b', 'm']
  hatch_map = ['/', '//', '\\', '\\\\', '-', '--', '+']
  for kernel in metrics_dict:
    if kernel == "dgrad_alg1_engine":
      n_groups = len(layer_list) - 1
    else:
      n_groups = len(layer_list)

    num_metrics = len(metrics_dict[kernel])

    index = np.arange(n_groups) * 1.5 * num_metrics * bar_width

    i = 0
    plt.figure()
    fig, ax = plt.subplots()
    for metric in metrics_dict[kernel]:
      ax.bar(index + i * bar_width, metrics_dict[kernel][metric], bar_width,
              alpha=opacity,
              color=color_map[i],
              edgecolor='black',
              hatch=hatch_map[i],
              label=metric)
      i += 1
  
    ax.set_xlabel('Layers')
    ax.set_ylabel('')
    
    ax.grid()
    ax.set_xticks(index + bar_width * num_metrics / 2)
    ax.set_xticklabels(layer_list[len(layer_list)-len(metrics_dict[kernel][metric]):])
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2,
               ncol=1, borderaxespad=0.)
    plt.tight_layout()
    plt.savefig(title+"_"+kernel+"_"+batch_size+'.pdf', format='pdf', bbox_inches='tight')

usage = "usage: %prog [option1] arg1,arg2 [option2] arg1,arg2"
def main():
  if len(sys.argv) == 1:
    print usage
    exit()

  parser = OptionParser(usage)
  parser.add_option("-n", "--batch-size", type="string", dest="batchsize",
                    help="Batch size seperated by coma", metavar="BATCH_SIZE")
  parser.add_option("-l", "--layer", type="string", dest="layername",
                    help="Layer names seperated by coma", metavar="LAYER")
  parser.add_option("-k", "--kernels", type="string", dest="kernels",
                    help="Kernels name seperated by coma", metavar="KERNELS")
  parser.add_option("-m", "--metrics", type="string", dest="metrics",
                    help="Metrics name seperated by coma", metavar="METRICS")
  parser.add_option("-t", "--title", type="string", dest="title",
                    help="Plot title", metavar="TITLE")

  (options, args) = parser.parse_args()
  if len(args) > 0:
    print "Arguments parsing fail. Possible reason: space occurred between arguments"
    exit()

  layer_list = []
  batchsize_list = []
  kernels_list = []
  metrics_list = []
  title = ""
  titles_list = ["CacheHitRate", "MemTransaction1", "MemTransaction2",\
                 "MemUtilization", "MemThroughput1", "MemThroughput2", "MemEfficiency"]
  if options.layername != None:
    layer_list = options.layername.split(",")
  num_layers = len(layer_list)
  if options.batchsize != None:
    batchsize_list = options.batchsize.split(",")
  if options.kernels != None:
    kernels_list = options.kernels.split(",")
  if options.metrics != None:
    metrics_list = options.metrics.split(",")
  if options.title != None:
    if options.title in titles_list:
      title = options.title

  ObtainMetricTraceFiles()
  
  GenerateMetricDict()
  if len(metric_trace_dict) == 0:
    print "NO trace found!!!"
    exit()

  is_kernel_list_empty = len(kernels_list) == 0
  for b_size in batchsize_list:
    if b_size not in metric_trace_dict:
      print " Batch size INVALID!!!"
      exit()
    print "For batch size: ", b_size
    for layer in layer_list:
      if layer not in metric_trace_dict[b_size]:
        print "Layer name INVALID!!!"
        exit()
      print "In layer: ", layer
      for propagation in metric_trace_dict[b_size][layer]:
        print "Propagation: ", propagation
        if is_kernel_list_empty:
          kernels_list = metric_trace_dict[b_size][layer][propagation]
        for kernel in kernels_list:
          if kernel not in metric_trace_dict[b_size][layer][propagation]:
            print "Kernel name INVALID!!!", kernel
            exit()
          print "   In Kernel: ", kernel
          for metric in metrics_list:
            if metric not in metric_trace_dict[b_size][layer][propagation][kernel]:
              print "Metric name: ", metric, " INVALID!!!"
              exit()
            value = metric_trace_dict[b_size][layer][propagation][kernel][metric]
            print "     Metric: ", metric," ", value 
  # Plot
  for batch_size in batchsize_list:
    PlotByLayerName(title, layer_list, batch_size, metrics_list)



if __name__ == '__main__':
  main()
