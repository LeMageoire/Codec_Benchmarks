#!/bin/sh

echo "This is a default benchmark script."
echo "main.py in python folder is the entry point for the benchmark."
echo "main.py is called with : "
echo "-i data/D"
echo "-c ./configs/default/config.json"
echo "-b ./benchmarks/default/config.json"
echo "output is defaulted to ./results/default/out.txt"

python3 python/main.py -i data/D -c ./configs/default/config.json -b ./benchmarks/default/config.json

echo "default Benchmark finished. Results are in /results/default/out.txt"
