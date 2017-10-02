#! /bin/bash

# Setup directories
WORK_DIR="$(pwd)"
TRACE_DIR=alexnet_results_pascal
FIGURE_DIR=${WORK_DIR}/${TRACE_DIR}/figures/
if [ ! -d "${FIGURE_DIR}" ]; then
  mkdir ${FIGURE_DIR}
fi

BATCH_SIZE_LIST=( 128 )
PROFILER=nvprof
ARCH=pascal
LAYERS=conv1,relu1,lrn1,pool1,conv2,relu2,lrn2,pool2,conv3,relu3,conv4,relu4,conv5,relu5,pool5,fc6,relu6,fc7,relu7,fc8,softmax
if [ "${TRACE_DIR}" == "alexnet_results_pascal" ]; then
  IPC_METRICS=executed_ipc

else
  IPC_METRICS=ipc

fi

for bs in ${BATCH_SIZE_LIST[@]}
do
  SCRIPT=${WORK_DIR}/nvprof_kernel_metric_trace_search_tool.py
  ${SCRIPT} -a ${ARCH} -d ${TRACE_DIR} -t CuUtilization  -l ${LAYERS} -n ${bs} -m ldst_fu_utilization,alu_fu_utilization,cf_fu_utilization,tex_fu_utilization
  ${SCRIPT} -a ${ARCH} -d ${TRACE_DIR} -t IPC  -l ${LAYERS} -n ${bs} -m ${IPC_METRICS}
  ${SCRIPT} -a ${ARCH} -d ${TRACE_DIR} -t ReplayRate  -l ${LAYERS} -n ${bs} -m inst_replay_overhead

  ${SCRIPT} -a ${ARCH} -d ${TRACE_DIR} -t Efficiency -l ${LAYERS} -n ${bs} -m issue_slot_utilization,flop_sp_efficiency

  ${SCRIPT} -a ${ARCH} -d ${TRACE_DIR} -t StallReason -l ${LAYERS} -n ${bs} -m stall_inst_fetch,stall_exec_dependency,stall_memory_dependency,stall_texture,stall_sync,stall_other,stall_pipe_busy,stall_constant_memory_dependency,stall_memory_throttle,stall_not_selected

  #${SCRIPT} -t FlopCountSP -l ${LAYERS} -n ${bs} -m flop_count_sp_add,flop_count_sp_mul,flop_count_sp_fma,flop_count_sp_special

done

#mv *.pdf ${FIGURE_DIR}
