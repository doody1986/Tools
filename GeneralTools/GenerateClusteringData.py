#! /usr/bin/env python

import sys
import csv
import numpy as np

def main():
  if len(sys.argv) < 4:
    print "The input argument should include number of cluster, number of "\
          "samples per cluster, and dimension"
    exit()

  k = int(sys.argv[1])
  num_samples_per_k = int(sys.argv[2])
  num_dim = int(sys.argv[3])

  print "Number of cluster: ", k
  print "Number of samples per cluster: ", num_samples_per_k
  print "Number of dimension: ", num_dim

  print "Start generating..."

  min_value = -1000
  max_value = 1000
  means = np.random.uniform(min_value, max_value, k)
  std = 5
  test_data = np.empty([num_samples_per_k * k, num_dim])
  f = open("clustering_k" + str(k) + "_" + str(num_samples_per_k) + "_d"+ str(num_dim) + ".txt", "w")
  for i in range(1, k+1):
    cluster_data = np.random.normal(means[i-1], std, [num_samples_per_k, num_dim])
    test_data[(i-1)*num_samples_per_k:i*num_samples_per_k] = cluster_data
    for row in range(0, cluster_data.shape[0]):
      for col in range(0, cluster_data.shape[1]):
        if col == cluster_data.shape[1] - 1:
          f.write(str(cluster_data[row][col]) + "\n")
        else:
          f.write(str(cluster_data[row][col]) + " ")
  f.close()
  
  print "End generating..."


if __name__ == '__main__':
  main()

