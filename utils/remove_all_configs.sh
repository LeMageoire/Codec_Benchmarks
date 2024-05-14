#!/bin/sh

echo "Removing all configs and benchmarks, except for the default one"
rm -rf ./benchmarks/2024*
rm -rf ./configs/2024*
echo "Done"