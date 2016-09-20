#! /usr/bin/env python

import sys
import re
import matplotlib.pyplot as plt
import collections

test_accuracy_dict = collections.OrderedDict()

usage = "Accept multiple results files from Cifar Mnist ImageNet etc."

def main():
  if len(sys.argv) < 2:
    print "Too few argument"
    print usage
    exit()


  file_name_list = sys.argv
  del file_name_list[0]
  if len(file_name_list) % 2 != 0:
    print "Number of arguments is not correct, please check carefully"
    print usage
    exit()

  print "File names processed: "
  print file_name_list

  print "Start..."
  regex_test_accuracy = re.compile(r"^I.*Test net output #0: accuracy = (\d+\.\d+)")

  # Extract corresponding label info
  labels = ['cifar', 'mnist']

  for file_name in file_name_list:
    # Open the file
    file_obj = open(file_name, "rb")

    test_accuracy_dict[file_name] = []
    for line in file_obj:
      if regex_test_accuracy.match(line):
        test_accuracy_dict[file_name].append(regex_test_accuracy.match(line).group(1))

    file_obj.close()

  prefix = 'averaged_accuracy_difference'
  

  # Extract the averaged accuracy
  # Only two GPU case is considered here
  step = 2
  accuracy_diff = []
  for i in range(0, len(test_accuracy_dict), step): 
    temp_accuracy_list_1 = map(float, test_accuracy_dict[file_name_list[i]])
    temp_accuracy_list_2 = map(float, test_accuracy_dict[file_name_list[i+1]])
    denominator = len(temp_accuracy_list_1)
    print denominator
    if len(temp_accuracy_list_1) != len(temp_accuracy_list_2):
      print "Something is wrong"
      exit()
    abs_diff = []
    for j in range(0, denominator):
      abs_diff.append(abs(temp_accuracy_list_1[j] - temp_accuracy_list_2[j]))
    print abs_diff
    accuracy_diff.append(sum(abs_diff) / denominator)

  print accuracy_diff

  # Generate plot
  plt.figure(1)

  bar_width = 0.15
  # index for accessing label and line pattern
  index = 0.25
  opacity = 1
  color = ['b', 'r']
  label = ['Cifar10 model', 'Mnist model']
  for i in range(0, len(accuracy_diff)):
    rects1 = plt.bar(index + i * 0.3, accuracy_diff[i], bar_width,
                     alpha=opacity,
                     color=color[i],
                     label=label[i])
  plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelbottom='off') # labels along the bottom edge are off

  plt.xlabel('Models')
  plt.ylabel('Averaged accuracy difference')

  plt.grid()
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
             ncol=3, mode="expand", borderaxespad=0.)

  plt.tight_layout()
  plt.savefig(prefix + '.png' , bbox_inches='tight')

  print "End..."


if __name__ == '__main__':
  main()
