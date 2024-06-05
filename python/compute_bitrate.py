import os
from collections import Counter
import argparse
import pathlib
import logging

def read_fasta(filename):
    """Reads a FASTA file and returns a dictionary of sequences keyed by sequence header."""
    sequences = {}
    with open(filename, 'r') as file:
        sequence = ''
        header = ''
        for line in file:
            line = line.strip()
            if line.startswith('>'):  # Sequence header
                if header:
                    sequences[header] = sequence
                    sequence = ''
                header = line[1:]  # Remove '>'
            else:
                sequence += line
        if header:
            sequences[header] = sequence
    return sequences

def count_nucleotides(sequences):
    """Counts the nucleotides in each sequence."""
    counts = Counter()
    for seq in sequences.values():
        counts.update(seq)
    return counts

def file_size_in_bytes(filename):
    """Returns the file size in bytes."""
    return os.path.getsize(filename)

def main():
    """
    this program outputs the complete nucleotide
    
    :param: -i the inputfile (original data in byte)
    :param: -o the .fasta file 
    """
    
    parser = argparse.ArgumentParser(description="Compute bitrate")
    parser.add_argument('--input1', '-i', dest='fin_bits', type=str, action='store', required=True, help='str filepath to original data')
    parser.add_argument('--input2', '-j', dest='fin_fasta',type=str, action='store', required=True, help='str filepath to fasta file')
    
    args = parser.parse_args()
    base_path = pathlib.Path(__file__).parent.parent.absolute()
    
    #Set up logger
    #logger = logging.getLogger('Results')
    #logger.setLevel(logging.DEBUG)
    
    original_text_file = str(base_path / args.fin_bits)
    transformed_fasta = str(base_path / args.fin_fasta)
    original_fasta = 'intermediates_files/2024-06-05_17-07-46/pkg_rep_0.0/noisy/noisy_0.0/noisy_0_0.0_0.0.fasta'
    #'str(base_path / args.fin_fasta)'

    # Read sequences from the FASTA file
    fasta_sequences = read_fasta(transformed_fasta)
    org_fasta_sequences = read_fasta(original_fasta)

    # Count nucleotides in the FASTA file
    fasta_counts = count_nucleotides(fasta_sequences)
    org_fasta_counts = count_nucleotides(org_fasta_sequences)
    # File sizes
    original_size = 8 * file_size_in_bytes(original_text_file)
    
    print("Original Text File Size in Bits:", original_size)
    # Calculate and print the total ratio of nucleotides to the original text file size
    total_nucleotides = sum(fasta_counts[nuc] for nuc in 'ACTG' if nuc in fasta_counts)
    total_org_nucleotides = sum(org_fasta_counts[nuc] for nuc in 'ACTG' if nuc in org_fasta_counts)
    print(f"Total Nucleotides in Transformed File: {total_nucleotides}")
    if original_size > 0:
        total_ratio = total_nucleotides / original_size
        org_total_ratio = (total_org_nucleotides / original_size)
        total_ratio = total_ratio
        relative_ratio = (abs(total_ratio - org_total_ratio)/org_total_ratio)*100
        print(f"Total Ratio of Nucleotides to Original Text File Size: {total_ratio:.6f}")
        print(f"Relative Ratio of Nucleotides to Original Text File Size: {relative_ratio:.6f}")
    else:
        print("Original text file size is zero, cannot calculate ratio.")

if __name__ == "__main__":
    main()
