
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
    py_command = ("{path}/.venv/bin/python {path}/libraries/Custom-DNA-Aeon/python/decode.py -c {config}").format(path=".", config="tmp_config.json")
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

def generate_ini_files(package_repetition, config, interfolder, dict_tmp_interfolder):
    """
    for every package repetition value we generate an .ini file and a .fasta file
    """
    for pkg in package_repetition:
        py_command = ("{path}/.venv/bin/python {path}/libraries/Custom-DNA-Aeon/python/encode.py -c {config}").format(path=".", config=config)
        process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
        output, error = process.communicate()
        process.wait()
        tmp_interfolder = interfolder / f"pkg_rep_{pkg}"
        os.mkdir(tmp_interfolder, exist_ok=True)
        try :
            shutil.copy("data/encoded.ini", tmp_interfolder / "encode.ini")
            os.remove("data/encoded.ini")
        except:
            print("no .ini to remove")
        try :
            shutil.copy("data/encoded.fasta", tmp_interfolder / "encode.fasta")
            os.remove("data/encoded.fasta")
        except:
            print("no .fasta to remove")
        dict_tmp_interfolder[str(pkg)] = tmp_interfolder
        os.mkdir(tmp_interfolder / "noisy", exist_ok=True)

def generate_noisy_fasta_files(error_rate, package_repetition, benchmark, dict_tmp_interfolder):
    """
    
    """
    for(err_rate, pkg_rep) in itertools.product(error_rate, package_repetition):
        for i in range(benchmark["args"]["num_iters"]):
            f_input = dict_tmp_interfolder[str(pkg_rep)] / "encode.fasta"
            py_command = ("{path}/.venv/bin/python {path}/simulation_framework.py -c 1 -i {input} -e {err_rate}").format(path=path.joinpath("libraries/fork-jpeg-dna-noise-models/v0.2"), input=f_input, err_rate=err_rate)
            process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
            output, error = process.communicate()
            process.wait()
            py_command = ("{path}/.venv/bin/python {path}/libraries/fork-jpeg-dna-noise-models/scripts/combine_consensus_and_original.py {original} {consensus}").format(path=".", original=f_input, consensus="/Users/mguyot/Documents/Codec_Benchmarks/libraries/jpeg-dna-noise-models/v0.2/output_fasta/consensus/consensus_encode_c1.fasta")
            process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
            output, error = process.communicate()
            process.wait()
            noisy_dir = dict_tmp_interfolder[str(pkg_rep)] / "noisy" / f"noisy_{err_rate}"
            os.mkdir(noisy_dir, exist_ok=True)
            noisy_file = "/Users/mguyot/Documents/Codec_Benchmarks/libraries/fork-jpeg-dna-noise-models/v0.2/output_fasta/consensus/combined.fasta"
            try :
                shutil.move(noisy_file, noisy_dir / f"noisy_{i}_{err_rate}_{pkg_rep}.fasta")
            except:
                print("src file not found so we can't move it")

def pipeline_benchmark(benchmark, config, ff_input, output, path, interfolder, folder_name, debug=False, skip_encode=False):
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
            generate_ini_files(package_repetition, config, interfolder, dict_tmp_interfolder)
            generate_noisy_files()
        else:
            decode_step(interfolder, config, error_rate, package_repetition, benchmark, nb_iter)
    return result

def setup_directories(base_path, codec_conf, bench_conf):
    # Generate a unique folder name based on the current timestamp
    folder_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Define paths for benchmarks and configs within the directory structure
    bench_folder = base_path / "benchmarks" / folder_name
    config_folder = base_path / "configs" / folder_name
    interfolder = base_path / "intermediates_files" / folder_name
    results_folder = base_path / "results" / folder_name
    
    # Create directories
    os.makedirs(bench_folder, exist_ok=True)
    os.makedirs(config_folder, exist_ok=True)
    os.makedirs(interfolder, exist_ok=True)
    os.makedirs(results_folder, exist_ok=True)
    
    # Save configurations
    bench_file = bench_folder / "config.json"
    config_file = config_folder / "config.json"
    
    save_configuration(bench_file, bench_conf)
    save_configuration(config_file, codec_conf)
    
    return bench_file, config_file, interfolder, results_folder

def save_configuration(file_path, data):
    # Save JSON data to a file
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def main():
    """
    :param: the input file to process (the file to encode + noisy + decode)
    :param: the output file to store the results 
    :param: the config file to load the codec (json file)
    :param: the benchmarks file to load the benchmarks (json file)
    """
    parser = argparse.ArgumentParser(description="Provide a file to process and store the results in an output file")
    parser.add_argument('--input', '-i', dest='fin', type=str, action='store', help="input file", required=True)
    parser.add_argument('--output', '-o', dest='fout', type=str, action='store', required=False, default="/default/out.txt", help="output file to store the results")
    # argument is json_path file (config of codec), will be later given in the benchmark file for flexibility
    parser.add_argument("--config", '-c', dest="codec_conf", required=True , help="config file")
    # argument is json_path file (config of benchmarks)
    parser.add_argument("--benchmarks", '-b', dest='bench_conf', type=str, action='store', required=True, help="benchmarks file")
    parser.add_argument("--debug", '-d', dest='debug', action='store_true', help="debug mode")
    # add a default mode for a demonstration purpose
    # parser.add_argument("--default", '-d', dest='default', type=bool, action='store_true', help="default mode")
    args = parser.parse_args()
    base_path = pathlib.Path(__file__).parent.parent.absolute()
    results = []
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    if(args.debug):
       print("\ndefault mode\n")
    with open(str(args.codec_conf), "r") as f:
        codec_conf = json.load(f)
    # load the benchmarks file
    with open(str(args.bench_conf), "r") as f:
        bench_conf = json.load(f)
    folder_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    bench_file, config_file, interfolder, results_folder = setup_directories(base_path, codec_conf, bench_conf)
    results = pipeline_benchmark(bench_file, config_file, args.fin, args.fout, base_path, interfolder, folder_name, args.debug)
    print(f"results will be stored in results.json in {results_folder}".format(results_folder))
    with open(results_folder / "results.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()