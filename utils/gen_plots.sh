#!/bin/sh

# if the results are already in the results folder, then we can generate the plots
echo "Generating plots..."
echo "python3 python/gen_plot.py --dir results/{$1}"
python3 python/gen_plot.py --dir results/$1
echo "Plots generated in the results folder in results/{$1}/plots folder."
echo "Plots are:"
echo "1. % success rate vs (error_rate, pkg_redundancy)"
echo "2. bitrate vs (error_rate, pkg_redundancy)"
echo "Done."