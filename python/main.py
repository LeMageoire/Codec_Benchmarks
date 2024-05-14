
import argparse
import subprocess
import pathlib
import os
import sys
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import itertools
import time
import shutil

def pipeline_benchmark(benchmark, config, input, output, path, interfolder, folder_name, debug=False):
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
    # load the json files
    with open(benchmark, "r") as f:
        b_file = json.load(f)
    with open(config, "r") as f:
        c_file = json.load(f)
    dict_tmp_interfolder = {} #should be a dict of files and the key is the pkg_rep value as a string
    results = [] # dict of results
    result = [] # dict of result
    for benchmark in b_file["benchmarks"]:
        nb_iter = int(benchmark["args"]["num_iters"])
        error_rate = np.linspace(benchmark["args"]["error_rate_min"], benchmark["args"]["error_rate_max"], int((benchmark["args"]["error_rate_step"])))
        package_repetition = np.linspace(benchmark["args"]["package_redundancy_min"], benchmark["args"]["package_redundancy_max"], int((benchmark["args"]["package_redundancy_step"])))
        for pkg in package_repetition:
            #we have to update the config file (valid)
            #if __debug__:
            #    # I need absolute path for input and output
            #    c_file["NOREC4DNA"]["package_redundancy"] = pkg
            #    c_file["encode"]["input"] = str(path) + "/" + input
            #    c_file["encode"]["output"] = str(path) + "/encode.fasta"
            #    with open(config, "w") as f:
            #        json.dump(c_file, f)
            #to be solved but encode.py will stock encode.ini and encode.fasta at root of the DNA-Aeon folder
            #and data/D is not taken into account
            if(debug):
                #py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/encode.py -c {config} -i {input} -o {output} -m {sys}").format(path=".", config=config, input=input, output=output, sys="sys")
                py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/encode.py -c {config} -m {sys}").format(path=".", config=config, sys="sys")
            else :
                #py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/encode.py -c {config} -i {input} -o {output}").format(path=".", config=config, input=input, output=output)
                py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/encode.py -c {config}").format(path=".", config=config)
            if(debug):
                process = subprocess.Popen(py_command.split(" "), stdout=sys.stdout, stderr=sys.stderr)
            else:
                process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
            output, error = process.communicate()
            process.wait()
            exit(0)
            tmp_interfolder = interfolder.joinpath("pkg_rep_" + str(pkg))
            os.mkdir(tmp_interfolder)
            shutil.copy("encode.ini", tmp_interfolder.joinpath("encode.ini"))
            os.remove("encode.ini")
            shutil.copy("encode.fasta", tmp_interfolder.joinpath("encode.fasta"))
            os.remove("encode.fasta")
            dict_tmp_interfolder[str(pkg)] = tmp_interfolder
            os.mkdir(tmp_interfolder.joinpath("noisy"))
            exit(0)
        exit(0)
        return "pkg_rep done"
        for (err_rate, pkg_rep) in itertools.product(error_rate, package_repetition):
            for i in range(benchmark["args"]["num_iter"]):
                f_input = dict_tmp_interfolder[str(pkg_rep)].joinpath("encode.fasta") 
                py_command = ("{path}/.venv/bin/python {path}/libraries/jpeg-dna-noise-models/v0.2/simulation_framework.py -c 1 -i {input} -o {output} -e {err_rate}").format(path=path, input=f_input, output=output, err_rate=err_rate)
                process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
                output, error = process.communicate()
                process.wait()
                # store the noisy channel file in the interfolder/tmp_interfolder/noisy folder
                os.move("output_fasta", dict_tmp_interfolder[str(pkg_rep)].joinpath("/noisy/").joinpath("noisy_"+str(i)+'_'+str(err_rate)+'_'+str(pkg_rep)+".fasta"))
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
    parser.add_argument("--debug", '-d', dest='debug', action='store_true', help="debug mode")
    # add a default mode for a demonstration purpose
    # parser.add_argument("--default", '-d', dest='default', type=bool, action='store_true', help="default mode")
    args = parser.parse_args()
    # use pathlib to get the project directory (done)
    path = pathlib.Path(__file__).parent.parent.absolute()
    results = []
    # load the config file
    if(args.debug):
       print("\ndefault mode\n")
    with open(str(args.codec_conf), "r") as f:
        codec_conf = json.load(f)
    # load the benchmarks file
    with open(str(args.bench_conf), "r") as f:
        bench_conf = json.load(f)
    folder_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    bench_folder = path.joinpath(str(path) + "/benchmarks/" + folder_name)
    os.mkdir(bench_folder)
    with open(bench_folder.joinpath("config.json"), "w") as f:
        json.dump(bench_conf, f)
    bench_file = bench_folder.joinpath("config.json")
    config_folder = path.joinpath(str(path) + "/configs/" + folder_name)
    os.mkdir(config_folder)
    with open(config_folder.joinpath("config.json"), "w") as f:
        json.dump(codec_conf, f)
    config_file = config_folder.joinpath("config.json")
    interfolder = path.joinpath(str(path) + "/intermediates_files/" + folder_name)
    os.mkdir(interfolder)
    results = pipeline_benchmark(bench_file, config_file, args.fin, args.fout, path, interfolder, folder_name, args.debug)
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