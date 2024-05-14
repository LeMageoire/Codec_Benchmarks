
import argparse
import subprocess
import pathlib
import os
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import itertools
import time

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
    
def pipeline_benchmark(benchmark, config, input, output, path, interfolder):
    """
    should benchmark every combination of error rate and package repetition of the codec
    
    - encoding implies :
        - calling encode.py with a updated config file,
        - we have to store .ini and .fasta files
    - noisy channel implies :
        - for every error_rate we have to generate a noisy channel file
            - then we have to store 
        - for every combination of error_rate and package repetition we have to generate 100 noisy channel file
    - decoding implies :
        - calling decode.py with a updated config file
        - we have to do it 100 times
        - we have to store the decoded file
    - evaluating implies :
        - for every decoded file we have to evaluate the ratio of success
        - for every decoded file we have to evaluate the time of execution
        - we have to store the results
    - result should be a dict with the following format :
    # "benchmark_name": "benchmark1",
    # { "success": True,
    #   "error_rate": 0.1, (the one given by the noise simulation)
    #   "elapsed_time": 0.1
    # }

    :benchmark: the benchmark to process
    :config: the config file to load the codec
    :input: the input file to process
    :output: the output file to store the results
    """
    nb_iter = int(benchmark["args"]["num_iter"])
    results = [] # dict of results
    result = [] # dict of result
    # benchmark is a dict
    files_path = {"ini": "", "fasta": ""}
    for benchmark in benchmark["benchmarks"]:
        error_rate = np.linspace(benchmark["args"]["error_rate_min"], benchmark["args"]["error_rate_max"], int((benchmark["args"]["error_rate_step"])))
        package_repetition = np.linspace(benchmark["args"]["package_redundancy_min"], benchmark["args"]["package_redundancy_max"], int((benchmark["args"]["package_redundancy_step"])))
        for pkg in package_repetition:
            #call encode.py to genrate the .fasta file and .ini file that should be stored under
            pkg_files = {"pkg_rep": {"ini": "", "fasta": ""}}
            pass
        for (err_rate, pkg_rep) in itertools.product(error_rate, package_repetition):
            for i in range(benchmark["args"]["num_iter"]):
                # use pkg_rep .ini and .fasta files
                f_input = pkg_files["pkg_rep"]["fasta"]
                py_command = ("{path}/.venv/bin/python {path}/libraries/jpeg-dna-noise-models/v0.2/simulation_framework.py -c 1 -i {input} -o {output} -e {err_rate}").format(path=path, input=f_input, output=output, err_rate=err_rate)
                process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
                output, error = process.communicate()
                # every file output of subprocess should be stored and = input of the next subprocess
                # check that subprocess is done and okay before calling the next one
            # you stored n_iter files, you have to decode them
            decoded_correctly = 0
            results.append({"benchmark_name": benchmark["name"]})
            for i in range(benchmark["args"]["num_iter"]):
                # we have to update the config file (make a copy of the original one)
                with open(config, "r") as f:
                    config = json.load(f)
                    tmp_config = json.loads(config)
                tmp_config["decode"]["input"] = ""
                tmp_config["decode"]["output"] = ""
                tmp_config["decode"]["metric"]["fano"]["error_probability"] = err_rate
                tmp_config["NOREC4DNA"]["package_redundancy"] = pkg_rep
                #store the tmp_config in a new file
                with open("tmp_config.json", "w") as f:
                    json.dump(tmp_config, f)
                py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/decode.py -c {config} -i {input} -o {output}").format(path=".", config=config, input=input, output=output)
                start_time = time.time()
                process = subprocess.Popen(py_command.split(), stdout=subprocess.PIPE)
                output, error = process.communicate()
                # rm the config file (the one updated) 
                process.wait()
                end_time = time.time()
                delta_time = end_time - start_time
                os.remove("tmp_config.json")
                try:
                    with open(output, "r") as f:
                        
                        decoded_correctly = (decoded_correctly + 1)/nb_iter
                except:
                    pass
                # 
                result.append({"iter" : i,"success": decoded_correctly, "error_rate": err_rate, "elapsed_time": delta_time, "pkg_rep": pkg_rep})
            results.append(result)
            



        
                
            

    # the idea is : changing the error rate doesn't need to be re-encoded so we need to encode for all pkg_rep
    # use functional programming with zip to iterate over the error rate and package repetition
    #for pkg_rep in benchmark["args"]["package_repetition"]:
    #    print("calling encode.py")
    #    py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/encode.py -c {config} -i {input} -o {output}").format(path=".", config=config, input=input, output=output)
    #    process = subprocess.Popen(py_command.split(), stdout=subprocess.PIPE)
    #    output, error = process.communicate()
    #    print("encode.py is done")
    #for error_rate in benchmark["args"]["error_rate"]:
    #    for i in range(benchmark["args"]["num_iter"]): 
    #        print("calling noisy_channel.py")
    #        # we have to call the encode (at path: ./libraries/DNA-Aeon/python/encode.py with parameters: -c path_to_config)
    #        py_command = ("{path}/.venv/bin/python {path}/libraries/jpeg-dna-noise-models/v0.2/simulation_framework.py -c {config} -i {input} -o {output}").format(path=".", config=config, input=input, output=output)
    #   process = subprocess.Popen(py_command.split(), stdout=subprocess.PIPE)
    #        output, error = process.communicate()
    #        print("noisy_channel.py is done")
    #         print("calling decode.py")
    #         # we have to call decode.py (at path: ./libraries/DNA-Aeon/python/decode.py with parameters: -c path_to_config)
    #         py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/decode.py -c {config} -i {input} -o {output}").format(path=".", config=config, input=input, output=output)
    #         time_start = time.time()
    #         process = subprocess.Popen(py_command.split(), stdout=subprocess.PIPE)
    #         output, error = process.communicate()
    #         time_end = time.time()
    #         print("decode.py is done")
    #         # we have to evaluate the results (error rate, time of execution, ratio of success)
    #         if decoded_correctly:
    #             result["benchmark_name"]["success"] = True
    #         else:
    #             result["benchmark_name"]["success"] = False
    #         result["benchmark_name"]["error_rate"] = error_rate
    #         result["benchmark_name"]["time"] = time_end - time_start
    # # aggregate the number of decoded file + % of success

    return result

def main():
    """
    :param: the input file to process (the file to encode + noisy + decode)
    :param: the output file to store the results 
    :param: the config file to load the codec (json file)
    :param: the benchmarks file to load the benchmarks (json file)
    """
    parser = argparse.ArgumentParser(description="Provide a file to process and store the results in an output file")
    parser.add_argument('--input', '-i', dest='fin', type=str, action='store', help="input file", required=True)
    parser.add_argument('--output', '-o', dest='fout', type=str, action='store', required=False, default="results/default/out.txt", help="output file to store the results")
    # argument is json_path file (config of codec), will be later given in the benchmark file for flexibility
    parser.add_argument("--config", '-c', dest="codec_conf", required=True , help="config file")
    # argument is json_path file (config of benchmarks)
    parser.add_argument("--benchmarks", '-b', dest='bench_conf', type=str, action='store', required=True, help="benchmarks file")
    args = parser.parse_args()
    # use pathlib to get the project directory (done)
    path = pathlib.Path(__file__).parent.parent.absolute()
    # load the config file
    with open(args.codec_conf, "r") as f:
        codec_conf = json.load(f)
    # load the benchmarks file
    with open(args.bench_conf, "r") as f:
        bench_conf = json.load(f)
    folder_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    interfolder = path.joinpath(str(path) + "/intermediates_files/" + folder_name)
    os.mkdir(interfolder)
    results = []
    #results = pipeline_benchmark(bench_conf, codec_conf, args.fin, args.fout, path, interfolder)
    newfolder = path.joinpath(str(path) + "/results/" + folder_name)
    os.mkdir(newfolder)
    if(args.fout != "results/default/out.txt"):
        output_path = newfolder.joinpath("results.txt")
    else :
        os.mkdir(path.joinpath(str(path) + "/results/default"))
        output_path = args.fout
    with open(output_path, "w") as f:
        f.write('\n'.join(results))
    
if __name__ == "__main__":
    main()