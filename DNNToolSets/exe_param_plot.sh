#! /bin/bash

if [ $# -eq 1 ]; then
  echo "Archtecture:" $1
else
  echo "Usage: ./<script> <arch>"
  exit
fi

# Setup directories
WORK_DIR="$(pwd)"
ARCH=$1
FIGURE_DIR=${WORK_DIR}/alexnet_gpu_trace/figures/
if [ ! -d "${FIGURE_DIR}" ]; then
  mkdir ${FIGURE_DIR}
fi

BATCH_SIZE_LIST=( 16,64,128 )

SCRIPT=${WORK_DIR}/nvprof_gpu_trace_search_tool.py
${SCRIPT} -a ${ARCH} -d alexnet_gpu_trace -c Plot -t RunningTime -n ${BATCH_SIZE_LIST}
${SCRIPT} -a ${ARCH} -d alexnet_gpu_trace -c Plot -t BlockSize -n ${BATCH_SIZE_LIST}
${SCRIPT} -a ${ARCH} -d alexnet_gpu_trace -c Plot -t NumRegister -n ${BATCH_SIZE_LIST}
${SCRIPT} -a ${ARCH} -d alexnet_gpu_trace -c Plot -t SharedMemSize -n ${BATCH_SIZE_LIST}

