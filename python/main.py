
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

def decode_iter(config, pkg_rep, err_rate, i, nb_iter, decoded_correctly, j, logger):
    """
    decode a single file and if it's decoded correctly increment the counter
    note: the config file is hardcoded for now
    note: we can tweak the full decode
    note: we could add the time of execution

    """
    logger.info("iteration: " + str(i))
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
    logger.info("calling decode.py")
    process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
    #process = subprocess.Popen(py_command.split(" "), stdout=sys.stdout, stderr=sys.stderr)
    output, error = process.communicate()
    logger.info("decode.py is done")
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
        logger.info("decoded correctly")
        decoded_correctly = ((decoded_correctly + 1)/nb_iter) * 100
        logger.info(decoded_correctly)
    with open("results.txt", "a") as f:
        f.write("decoded correctly: "+ str(j) + " " + str(i)+ "%\n")
        f.flush()
    try :
        os.remove("./data/D")
    except:
        print("no file to remove")
    logger.info("one iteration done")

def decode_step(interfolder, config, error_rate, package_repetition, benchmark, nb_iter, logger):
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
    logger.debug(interfolder)
    logger.debug(config)
    noisy_dir = "/Users/mguyot/Documents/Codec_Benchmarks/intermediates_files/2024-05-22_11-55-42"
    logger.info("shortcut => we go to decode directly")
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
        logger.info("100 decodes done")
        with open("results.txt", "a") as f:
            f.write("decoded correctly: " + str(decoded_correctly) + "%\n")
            f.flush()
        logger.info("all the decodes are done")

def generate_ini_files(package_repetition, config, interfolder, dict_tmp_interfolder, base_path, logger):
    """
    for every package repetition value we generate an .ini file and a .fasta file
    """
    venv_path = base_path / '.venv' / 'bin' / 'python'
    encode_script_path = base_path / 'libraries' / 'Custom-DNA-Aeon' / 'python' / 'encode.py'

    for pkg in package_repetition:
        logger.info(f"Generating ini files for package repetition {pkg}")
        py_command = f"{venv_path} {encode_script_path} -c {config}"
        process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
        output, error = process.communicate()
        process.wait()
        logger.info("encode.py is done")
        tmp_interfolder = interfolder / f"pkg_rep_{pkg}"
        os.makedirs(tmp_interfolder, exist_ok=True)
        try:
            shutil.copy(base_path / "data/encoded.ini", tmp_interfolder / "encode.ini")
            os.remove(base_path / "data/encoded.ini")
        except FileNotFoundError:
            print("No .ini file to remove.")
        
        try:
            shutil.copy(base_path / "data/encoded.fasta", tmp_interfolder / "encode.fasta")
            os.remove(base_path / "data/encoded.fasta")
        except FileNotFoundError:
            print("No .fasta file to remove.")
        dict_tmp_interfolder[str(pkg)] = tmp_interfolder
        os.makedirs(tmp_interfolder / "noisy", exist_ok=True)
        logger.info("ini files are generated")

def generate_noisy_fasta_files(error_rate, package_repetition, benchmark, dict_tmp_interfolder, base_path, logger):
    """
    Generate noisy FASTA files by applying error rates to encoded FASTA files.
    """
    for err_rate, pkg_rep in itertools.product(error_rate, package_repetition):
        logger.info(f"Generating noisy files for error rate {err_rate} and package repetition {pkg_rep}")
        venv_path = base_path / 'libraries' / 'fork-jpeg-dna-noise-models' / 'v0.2' / '.venv' / 'bin' / 'python'
        simulation_framework_path = base_path / 'libraries' / 'fork-jpeg-dna-noise-models' / 'v0.2' / 'simulation_framework.py'
        lib_path = base_path / 'libraries' / 'fork-jpeg-dna-noise-models' 
        combine_script_path = base_path / lib_path / 'scripts' / 'combine_consensus_and_original.py'
        consensus_path = base_path / lib_path / 'v0.2' / 'output_fasta' / 'consensus' / 'consensus_encode_c1.fasta'
        for i in range(benchmark["args"]["num_iters"]):
            logger.info(f"Iteration {i}")
            f_input = dict_tmp_interfolder[str(pkg_rep)] / "encode.fasta"
            py_command = f"{venv_path} {simulation_framework_path} -c 1 -i {f_input} -e {err_rate}"
            process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
            output, error = process.communicate()
            process.wait()
            logger.info("simulation_framework.py is done")
            py_command = f"{venv_path} {combine_script_path} {f_input} {consensus_path}"
            process = subprocess.Popen(py_command.split(" "), stdout=subprocess.PIPE)
            output, error = process.communicate()
            process.wait()
            logger.info("combine_consensus_and_original.py is done")
            noisy_dir = dict_tmp_interfolder[str(pkg_rep)] / "noisy" / f"noisy_{err_rate}"
            os.makedirs(noisy_dir, exist_ok=True)
            noisy_file = base_path / lib_path / 'v0.2' / 'output_fasta' / 'consensus' / 'combined.fasta'
            try:
                shutil.move(noisy_file, noisy_dir / f"noisy_{i}_{err_rate}_{pkg_rep}.fasta")
            except FileNotFoundError:
                print("Source file not found; cannot move it.")
            logging.info("noisy file is generated")

def pipeline_benchmark(benchmark, config, ff_input, output, base_path, interfolder, folder_name, logger ,debug=False, skip_encode=False):
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
            logger.info("generate_ini_files")
            generate_ini_files(package_repetition, config, interfolder, dict_tmp_interfolder, base_path, logger)
            logger.info("all the ini files are generated")
            logger.info("generate_noisy_fasta_files")
            generate_noisy_fasta_files(error_rate, package_repetition, benchmark, dict_tmp_interfolder, base_path, logger)
            logger.info("all the noisy files are generated => ready for decode")
        else:
            decode_step(interfolder, config, error_rate, package_repetition, benchmark, nb_iter, logger)
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

def corr_codec_conf(codec_conf, base_path):
    codec_conf["decode"]["input"] = str(base_path / "data/encoded.fasta")
    codec_conf["decode"]["NOREC4DNA_config"] = str(base_path / "data/encoded.ini")
    codec_conf["decode"]["output"] = str(base_path / "data/decoded.txt")
    codec_conf["encode"]["input"] = str(base_path / "data/D")
    codec_conf["encode"]["output"] = str(base_path / "data/encoded.fasta")
    codec_conf["general"]["codebook"]["motifs"] = str(base_path / "configs/codewords/cw_40_60_hp3.json")
    codec_conf["general"]["codebook"]["words"] = str(base_path / "configs/codewords/cw_40_60_hp3.fasta")

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
    # Set up logger
    logger = logging.getLogger('MyLogger')
    logger.setLevel(logging.DEBUG)  # Capture all levels of messages
    # Create handlers
    file_handler = logging.FileHandler(base_path / "debug/codec_benchmarks.log")
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG) 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    if(args.debug):
       print("\ndefault mode\n")
    with open(str(args.codec_conf), "r") as f:
        codec_conf = json.load(f)
    # load the benchmarks file
    with open(str(args.bench_conf), "r") as f:
        bench_conf = json.load(f)
    corr_codec_conf(codec_conf, base_path)
    folder_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logger.info("folder name: " + folder_name)
    logger.info(codec_conf)
    bench_file, config_file, interfolder, results_folder = setup_directories(base_path, codec_conf, bench_conf)
    logger.info("directories are set up")
    logger.info("start the pipeline")
    results = pipeline_benchmark(bench_file, config_file, args.fin, args.fout, base_path, interfolder, folder_name, logger, args.debug)
    print(f"results will be stored in results.json in {results_folder}".format(results_folder))
    with open(results_folder / "results.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()