#!/bin/bash

# tested vllm version: 0.7.3

export VLLM_ALLOW_LONG_MAX_MODEL_LEN=1 

model=${1:-Qwen/Qwen2.5-VL-7B-Instruct}
max_model_len=${2:-32768} 
gpu_memory_utilization=${3:-0.9}
devices=${4:-"0,1,2,3"}
tp_size=$(awk -F',' '{print NF}' <<< "$devices")
port=${5:-8964}

CUDA_VISIBLE_DEVICES=${devices} python -m vllm.entrypoints.openai.api_server \
    --model ${model} \
    --tensor_parallel_size ${tp_size} \
    --gpu_memory_utilization ${gpu_memory_utilization} \
    --port ${port} \
    --max_model_len ${max_model_len} \
