#! /usr/bin/env python

import sys
import re
import matplotlib.pyplot as plt
import collections

training_loss_dict = collections.OrderedDict()
test_accuracy_dict = collections.OrderedDict()
test_loss_dict = collections.OrderedDict()

usage = "Accept multiple results files"

def main():
  if len(sys.argv) < 2:
    print "Too few argument"
    print usage
    exit()

  file_name_list = sys.argv
  del file_name_list[0]
  print "File names processed: "
  print file_name_list

  print "Start..."
  regex_training_loss = re.compile(r"^I.*Iteration (\d+), loss = (\d+\.\d+)")
  regex_test_accuracy = re.compile(r"^I.*Test net output #0: accuracy = (\d+\.\d+)")
  regex_test_loss = re.compile(r"^I.*Test net output #1: loss = (\d+\.\d+)")

  # Only support two type of SGD for now
  labels = ['normal SGD', 'A-SGD']
  line_pattern = ['b-', 'r--']

  for file_name in file_name_list:
    # Open the file
    file_obj = open(file_name, "rb")

    training_loss_dict[file_name] = []
    test_loss_dict[file_name] = []
    test_accuracy_dict[file_name] = []
    training_loss = 0.0;
    test_loss = 0.0;
    for line in file_obj:
      if regex_training_loss.match(line):
        if training_loss == 0.0:
          training_loss = float(regex_training_loss.match(line).group(2))
        else:
          training_loss = 0.8 * training_loss + \
                          0.2 * float(regex_training_loss.match(line).group(2))
      if regex_test_loss.match(line):
        if test_loss == 0.0:
          test_loss = float(regex_test_loss.match(line).group(1))
        else:
          test_loss = 0.8 * test_loss + \
                      0.2 * float(regex_test_loss.match(line).group(1))

      if regex_test_accuracy.match(line) and training_loss != 0.0:
        test_accuracy_dict[file_name].append(regex_test_accuracy.match(line).group(1))
        training_loss_dict[file_name].append(training_loss)
        test_loss_dict[file_name].append(test_loss)

    file_obj.close()

  prefix = file_name_list[0].split('.')[0]

  # Generate plot
  plt.figure(1)
  # index for accessing label and line pattern
  idx = 0
  for key in training_loss_dict:
    plt.plot(training_loss_dict[key], line_pattern[idx],
           label=labels[idx],
           linewidth=2)
    idx += 1
  plt.xlabel('Normalized Iterations')
  plt.ylabel('Traning Loss')
  plt.grid()
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
             ncol=3, mode="expand", borderaxespad=0.)

  plt.tight_layout()
  plt.savefig(prefix + '_training_loss.png', bbox_inches='tight')

  plt.figure(2)
  # index for accessing label and line pattern
  idx = 0
  for key in test_loss_dict:
    plt.plot(test_loss_dict[key], line_pattern[idx],
           label=labels[idx],
           linewidth=2)
    idx += 1
  plt.xlabel('Normalized Iterations')
  plt.ylabel('Test Loss')
  plt.grid()
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
             ncol=3, mode="expand", borderaxespad=0.)

  plt.tight_layout()
  plt.savefig(prefix + '_test_loss.png', bbox_inches='tight')   

  plt.figure(3)
  # index for accessing label and line pattern
  idx = 0
  for key in test_accuracy_dict:
    plt.plot(test_accuracy_dict[key], line_pattern[idx],
           label=labels[idx],
           linewidth=2)
    idx += 1
  plt.xlabel('Normalized Iterations')
  plt.ylabel('Accuracy')
  plt.grid()
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
             ncol=3, mode="expand", borderaxespad=0.)

  plt.tight_layout()
  plt.savefig(prefix + '_accuracy.png', bbox_inches='tight')

  print "End..."


if __name__ == '__main__':
  main()
