#! /usr/bin/env python

import sys
import re
import matplotlib.pyplot as plt

training_loss_list = []
test_accuracy_list = []
test_loss_list = []

def main():
  if len(sys.argv) < 2:
    print "Too few argument"
    exit()

  if len(sys.argv) > 2:
    print "Too much argument"
    exit()

  file_name = sys.argv[1]
  print "File name processed: ", file_name

  # Open the file
  file_obj = open(file_name, "rb")

  print "Start..."

  regex_training_loss = re.compile(r"^I.*Iteration (\d+), loss = (\d+\.\d+)")
  regex_test_accuracy = re.compile(r"^I.*Test net output #0: accuracy = (\d+\.\d+)")
  regex_test_loss = re.compile(r"^I.*Test net output #1: loss = (\d+\.\d+)")

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
      test_accuracy_list.append(regex_test_accuracy.match(line).group(1))
      training_loss_list.append(training_loss)
      test_loss_list.append(test_loss)     

  file_obj.close()
  # Generate plot
  plt.figure(1)
  fig, ax1 = plt.subplots()
  ax1.set_ylabel('Loss')
  plt1 = plt.plot(training_loss_list, 'b-',
           label='Training loss',
           linewidth=2)
  plt2 = plt.plot(test_loss_list, 'b--',
           label='Test loss',
           linewidth=2)
  ax2 = ax1.twinx()
  plt3 = plt.plot(test_accuracy_list, 'r',
           label='Accuracy',
           linewidth=2)
  ax2.set_ylabel('Accuracy')
  ax2.set_ylim(0.0, 1.0)

  ax1.grid()
  ax1.set_xlabel('Normalized Iterations')
  
  plts = plt1 + plt2 + plt3
  labels = [l.get_label() for l in plts]

  plt.legend(plts, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
             ncol=3, mode="expand", borderaxespad=0.)

  plt.tight_layout()

  prefix = file_name.split('.')[0]
  plt.savefig(prefix + '.png', bbox_inches='tight')
  print "End..."


if __name__ == '__main__':
  main()
