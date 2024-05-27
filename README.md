# Codec_Benchmarks

The main goal is to provide an automated solution to benchmark coded

The idea would be :
- you gave the file , a config_file path for the codec config (.json) , a  
    - this would run the encoded.py with the config_file 
        - is has to be run only when one config parameters changes
            - like package redundancy and so on

## Notes
- this only works with python 3.9 because of NOREC4DNA libraries configuration
- care with commit version of submodules 


## Problem to be solved :

- [x] setting up NOREC4DNA libs in DNA-Aeon from this project repo
- [x] run one valid iteration codec
- [x] run the whole thing 

