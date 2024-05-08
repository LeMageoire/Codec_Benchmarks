
import argparse
import subprocess


import matplotlib.pyplot as plt

def gen_plots(result):
    """
    Generate the plots for the benchmark
    the results should holds :
    - the error rate for each iteration
    - the ratio of success for each iteration (decoded 100% correctly)
    - the time of execution for each iteration (average of the N iterations)

    - for each N simulations aggregated we should have two plots :
        - one with constant error rate showing the ratio of success for each package_repetition variation
        - one with constant package_repetition showing the ratio of success for each error rate variation
    
    :result: the result of the benchmark
    """

    # create 2 subplots with a global name of benchmark (for the title)
    fig, axs = plt.subplots(2)
    fig.suptitle("benchmark_name")
    # for the first subplot we have to plot the error rate for each iteration

    # for the second subplot we have to plot the ratio of success for each iteration
    
def pipeline_benchmark(benchmark, config, input, output):
    """
    pipeline of the benchmark
    this pipeline should process the whole benchmark
    
    - encode the input file
    - noisy channel the encoded file
    - decode the noisy channel file
    - evaluate the results

    for each 

    :benchmark: the benchmark to process
    :config: the config file to load the codec
    :input: the input file to process
    :output: the output file to store the results
    """

    # result should be a dict with the following format :
    # "benchmark_name": "benchmark1",
    # { "success": True,
    #   "error_rate": 0.1,
    #   "time": 0.1
    # }
    result = {} # dict of results
    # benchmark is a dict

    # the idea is : changing the error rate doesn't need to be re-encoded so we need to encode for all pkg_rep
    # use functional programming with zip to iterate over the error rate and package repetition
    for pkg_rep in benchmark["args"]["package_repetition"]):
        print("calling encode.py")
        py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/encode.py -c {config} -i {input} -o {output}").format(path=".", config=config, input=input, output=output)
        process = subprocess.Popen(py_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print("encode.py is done")
    for error_rate in benchmark["args"]["error_rate"]:
        for i in range(benchmark["args"]["num_iter"]): 
            print("calling noisy_channel.py")
            # we have to call the encode (at path: ./libraries/DNA-Aeon/python/encode.py with parameters: -c path_to_config)
            py_command = ("{path}/.venv/bin/python {path}/libraries/jpeg-dna-noise-models/v0.2/simulation_framework.py -c {config} -i {input} -o {output}").format(path=".", config=config, input=input, output=output)
            process = subprocess.Popen(py_command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print("noisy_channel.py is done")
            print("calling decode.py")
            # we have to call decode.py (at path: ./libraries/DNA-Aeon/python/decode.py with parameters: -c path_to_config)
            py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/decode.py -c {config} -i {input} -o {output}").format(path=".", config=config, input=input, output=output)
            time_start = time.time()
            process = subprocess.Popen(py_command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            time_end = time.time()
            print("decode.py is done")
            # we have to evaluate the results (error rate, time of execution, ratio of success)
            if decoded_correctly:
                result["benchmark_name"]["success"] = True
            else:
                result["benchmark_name"]["success"] = False
            result["benchmark_name"]["error_rate"] = error_rate
            result["benchmark_name"]["time"] = time_end - time_start
    # aggregate the number of decoded file + % of success

    return result




def extract_benchmarks(json_path):
    """
    Extract the benchmarks data from the json file
    the benchmarks has the following format:
    {
        "benchmarks": [
            {
                "name": "benchmark_name",
                "args": {
                    "arg1": "value1",
                    "arg2": "value2",
                    ...
                }
            },
            ...
        ]
    }

    we could use the json module to load the json file and extract the benchmarks data
    it could holds multiple benchmarks (for flexibility) but we will only use the first one for now
    :name: the name of the benchmark (for logging, automation of plotting)
    :args: the arguments of the benchmark (for automation of the benchmark)
            args1 is an error rate array
            args2 is a number of iterations
            args3 is package_repetition (is a % of overlapping in the dna sequence)
    """
    benchmarks = [] # dict of benchmarks
    # the dict should be recorded by benchmark name
    benchmarks.append({"name": "benchmark1", "args": {"arg1": "value1", "arg2": "value2"}})
    benchmarks.append({"name": "benchmark2", "args": {"arg1": "value1", "arg2": "value2"}})
    return benchmarks


def main():
    """
    test
    """
    parser = argparse.ArgumentParser(description="test")
    parser.add_argument("input", help="input file")
    parser.add_argument("output", help="output file")
    # argument is json_path file (config of codec), will be later given in the benchmark file for flexibility
    parser.add_argument("config", help="config file")
    # argument is json_path file (config of benchmarks)
    parser.add_argument("benchmarks", help="benchmarks file")
    args = parser.parse_args()
    print(args.input)
    print(args.output)

    # extract the benchmarks data from the json file
    benchmarks = extract_benchmarks(args.benchmarks)
    # for each benchmark we have to process the data (encode, noisy channel, decode, evaluate, store the results)
    results = []
    for benchmark in benchmarks:
        results.append(pipeline_benchmark(benchmark, args.config, args.input, args.output))
    # for each benchmark we have to store the results propose to store the results in a file
    
    # we have to generate the plots for the benchmarks
    for result in results:
        gen_plots(result)
        pass
    print("benchmarks are done : results are stored in the output file and plots are generated in the output folder")

if __name__ == "__main__":
    main()