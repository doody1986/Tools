#! /bin/bash

WORK_DIR="$(pwd)"
MEM_PLOT_SCRIPT=mem_plot.sh
COMPUTE_METRICS_PLOT_SCRIPT=compute_metric_plot.sh

ARCH_LIST=( kepler pascal )

for arch in ${ARCH_LIST[@]}
do
  ${WORK_DIR}/${MEM_PLOT_SCRIPT} ${arch}
  ${WORK_DIR}/${COMPUTE_METRICS_PLOT_SCRIPT} ${arch}
done
