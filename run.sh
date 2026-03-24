#!/bin/bash

# 激活 conda 虚拟环境
source activate weekly

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 运行主程序
python src/main.py "$@"
