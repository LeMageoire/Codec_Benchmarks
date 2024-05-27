
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
import logging

def decode_iter(config, pkg_rep, err_rate, i, nb_iter, decoded_correctly, j):
    """
    decode a single file and if it's decoded correctly increment the counter
    note: the config file is hardcoded for now
    note: we can tweak the full decode
    note: we could add the time of execution

    """
    logging.info("iteration: " + str(i))
    with open(config, "r") as f:
        j_config = json.load(f)
        j_config["decode"]["NOREC4DNA_config"] = "/Users/mguyot/Documents/Codec_Benchmarks/intermediates_files/2024-05-22_11-55-42/pkg_rep_" + str(pkg_rep) + "/encode.ini"
        j_config["decode"]["input"] = "/Users/mguyot/Documents/Codec_Benchmarks/intermediates_files/2024-05-22_11-55-42/pkg_rep_" + str(pkg_rep) + "/noisy"+"/noisy_" + str(err_rate) + "/noisy_" + str(i) + "_" + str(err_rate) + "_" + str(pkg_rep) + ".fasta"
        j_config["decode"]["output"] = "/Users/mguyot/Documents/Codec_Benchmarks/results/"+ str(i) + '_' + str(err_rate) + '_' + str(pkg_rep)  
        #tmp_config["decode"]["metric"]["fano"]["error_probability"] = err_rate
        j_config["NOREC4DNA"]["package_redundancy"] = pkg_rep
    with open("tmp_config.json", "w") as f:
        json.dump(j_config, f)
    py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/decode.py -c {config}").format(path=".", config="tmp_config.json")
    #py_command = ("{path}/.venv/bin/python {path}/libraries/DNA-Aeon/python/decode.py -c {config} -m {sys}").format(path=".", config="tmp_config.json", sys="sys")
    #start_time = time.time()
    logging.info("calling decode.py")
    process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
    #process = subprocess.Popen(py_command.split(" "), stdout=sys.stdout, stderr=sys.stderr)
    output, error = process.communicate()
    logging.info("decode.py is done")
    output_file = "/Users/mguyot/Documents/Codec_Benchmarks/results/"+ str(i) + '_' + str(err_rate) + '_' + str(pkg_rep) + "/decoded.fasta"
    process.wait()
    #end_time = time.time()
    #delta_time = end_time - start_time
    os.remove("tmp_config.json")
    py_command = ("{path}/.venv/bin/python {path}/python/compare_file.py -r {tocomp} -i {original}").format(path=".", tocomp="./data/D", original="./data/tmp/D")
    process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
    output, error = process.communicate()
    process.wait()
    if process.returncode == 0:
        logging.info("decoded correctly")
        decoded_correctly = ((decoded_correctly + 1)/nb_iter) * 100
        logging.info(decoded_correctly)
    with open("results.txt", "a") as f:
        f.write("decoded correctly: "+ str(j) + " " + str(i)+ "%\n")
        f.flush()
    try :
        os.remove("./data/D")
    except:
        print("no file to remove")
    logging.info("one iteration done")

def decode_step(interfolder, config, error_rate, package_repetition, benchmark, nb_iter):
    """
    this function is executing the decode.py for every noisy file generated
    for every combination of error rate and package repetition (cardinal_product)

    note: noisy_dir is hardcoded for now

    :param: interfolder: the folder where the noisy files are stored
    :param: config: the config file to load the codec
    :param: error_rate: the error rate to simulate
    :param: package_repetition: the package repetition to simulate
    :param: benchmark: the benchmark(.json file)
    """
    logging.debug(interfolder)
    logging.debug(config)
    noisy_dir = "/Users/mguyot/Documents/Codec_Benchmarks/intermediates_files/2024-05-22_11-55-42"
    logging.info("shortcut => we go to decode directly")
    j = 0
    skip_first = True
    for (err_rate, pkg_rep) in itertools.product(error_rate, package_repetition):
        print(f"\n ({err_rate},{pkg_rep}) \n".format(err_rate, pkg_rep)) 
        if skip_first :
            skip_first = False
            continue
        decoded_correctly = 0
        j += 1
        for i in range(benchmark["args"]["num_iters"]):
           decode_iter(config, pkg_rep, err_rate, i, nb_iter, decoded_correctly, j)
        logging.info("100 decodes done")
        with open("results.txt", "a") as f:
            f.write("decoded correctly: " + str(decoded_correctly) + "%\n")
            f.flush()
        logging.info("all the decodes are done")

def pipeline_benchmark(benchmark, config, ff_input, output, path, interfolder, folder_name, debug=False, skip_encode=True):
    """
    example of CLI command: python3 python/main.py -i data/D -c configs/config.json -b benchmarks/config.json
    :param: skip_encode: if True we skip the encoding part and go to encoding
    
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
        if not skip_encode:
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
                if __debug__:
                    print(interfolder)
                tmp_interfolder = interfolder.joinpath("pkg_rep_" + str(pkg))
                os.mkdir(tmp_interfolder)
                shutil.copy("data/encoded.ini", tmp_interfolder.joinpath("encode.ini"))
                os.remove("data/encoded.ini")
                shutil.copy("data/encoded.fasta", tmp_interfolder.joinpath("encode.fasta"))
                os.remove("data/encoded.fasta")
                dict_tmp_interfolder[str(pkg)] = tmp_interfolder
                os.mkdir(tmp_interfolder.joinpath("noisy"))
            if __debug__:
                print("all the encode.ini and encode.fasta are stored in the intermediates_files/timestamp_pkg_val folder")
            skip = True
            for (err_rate, pkg_rep) in itertools.product(error_rate, package_repetition):
                #logging.info(dict_tmp_interfolder.items())
                for i in range(benchmark["args"]["num_iters"]):
                    f_input = dict_tmp_interfolder[str(pkg_rep)].joinpath("encode.fasta") 
                    py_command = ("{path}/.venv/bin/python {path}/simulation_framework.py -c 1 -i {input} -e {err_rate}").format(path=path.joinpath("libraries/jpeg-dna-noise-models/v0.2"), input=f_input, err_rate=err_rate)
                    process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
                    #process = subprocess.Popen(py_command.split(), stdout=sys.stdout, stderr=sys.stderr)
                    output, error = process.communicate()
                    process.wait()
                    # we have to combine encoded "> " lines with noisy " " lines (interpolation)
                    if __debug__ : 
                        #wait for user input
                        #print("Press Enter to continue...")
                        #input()
                        print("calling combine_consensus_and_original.py")
                        #print(f"original: {f_input}")
                    py_command = ("{path}/.venv/bin/python {path}/libraries/jpeg-dna-noise-models/scripts/combine_consensus_and_original.py {original} {consensus}").format(path=".", original=f_input, consensus="/Users/mguyot/Documents/Codec_Benchmarks/libraries/jpeg-dna-noise-models/v0.2/output_fasta/consensus/consensus_encode_c1.fasta")
                    process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
                    # store the noisy channel file in the interfolder/tmp_interfolder/noisy folder
                    # inside the interfolder/tmp_interfolder/noisy we should add a folder named noisy_ + err_rate value
                    output, error = process.communicate()
                    process.wait()
                    noisy_dir = dict_tmp_interfolder[str(pkg_rep)].joinpath("noisy", "noisy_" + str(err_rate))
                    if not os.path.exists(noisy_dir):
                        os.mkdir(noisy_dir)
                    #we should check output_fasta name ?
                    noisy_file = "/Users/mguyot/Documents/Codec_Benchmarks/libraries/jpeg-dna-noise-models/v0.2/output_fasta/consensus/combined.fasta"
                    try :
                        shutil.move(noisy_file, noisy_dir.joinpath("noisy_"+str(i)+'_'+str(err_rate)+'_'+str(pkg_rep)+".fasta"))
                    except:
                        print("src file not found so we can't move it")
                if __debug__ :
                    print("100 noisy done we need it 25 times")
            logging.info("noisy done => we need to decode all thoses files")
        else:
            decode_step(interfolder, config, error_rate, package_repetition, benchmark, nb_iter)
        return "noisy_done"
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
    # Setup basic logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
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
        try:
            os.mkdir(path.joinpath(str(path) + "/results/default"))
        except:
            pass
        output_path = args.fout
    with open(output_path, "w") as f:
        f.write('\n'.join(results))
    
if __name__ == "__main__":
    main()