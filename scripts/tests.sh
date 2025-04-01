#!/bin/bash

data_folder=""
if [ $# -eq 1 ]; then
  data_folder="$1"
else
  echo "Error: Exactly one argument is required."
  exit 1
fi

log_folder=$(date +%Y%m%d_%H%M%S)
mkdir "logs/$log_folder"

# trace_files=("DS1.lis" "OLTP.lis" "S1.lis" "S2.lis" "S3.lis")
# trace_file_dbnames=("ds1" "oltp" "s1" "s2" "s3")

trace_files=("test1.txt")
trace_file_dbnames=("test1")

cache_types=("1" "2" "3" "4")

for cache_type in "${cache_types[@]}"; do
    for i in "${!trace_files[@]}"; do
      python3 app/app.py $data_folder/"${trace_files[$i]}" "${trace_file_dbnames[$i]}" --cache_type=$cache_type --thread_count=2 --log_dir=logs/$log_folder
    done
done
