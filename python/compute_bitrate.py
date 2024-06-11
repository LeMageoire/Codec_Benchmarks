import os
from collections import Counter
import argparse

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
    parser = argparse.ArgumentParser(description="Calculate the ratio of nucleotides to the original text file size in [bit/nt]")
    parser.add_argument('--original', '-o', dest='original_text_file',required=True ,help="Path to the original text file")
    parser.add_argument('--transformed', '-t', dest='transformed_fasta', required=True, help="Path to the transformed FASTA file (noisy_decoded + successfully decoded)")
    parser.add_argument('--original_fasta', '-of', dest='original_fasta', required=True, help="Path to the original FASTA file (not noisy)")
    parser.add_argument('--noindels', '-ni', dest='noindels', action='store_true', help="Ignore indels")
    args = parser.parse_args()

    original_text_file = args.original_text_file
    transformed_fasta = args.transformed_fasta
    original_fasta = args.original_fasta

    # Read sequences from the FASTA file
    fasta_sequences = read_fasta(transformed_fasta)
    org_fasta_sequences = read_fasta(original_fasta)

    # Count nucleotides in the FASTA file
    fasta_counts = count_nucleotides(fasta_sequences)
    org_fasta_counts = count_nucleotides(org_fasta_sequences)
    # File sizes
    original_size = 8 * file_size_in_bytes(original_text_file)
    
    print("Original Text File Size in Bits:", original_size)
    print("Nucleotide Counts in Transformed File:", fasta_counts)
    print("Nucleotide Counts in Original File:", org_fasta_counts)
    # Calculate and print the total ratio of nucleotides to the original text file size
    total_nucleotides = sum(fasta_counts[nuc] for nuc in 'ACTG' if nuc in fasta_counts)
    total_org_nucleotides = sum(org_fasta_counts[nuc] for nuc in 'ACTG' if nuc in org_fasta_counts)
    print(f"Total Nucleotides in Transformed File: {total_nucleotides}")
    if original_size > 0:
        total_ratio = total_nucleotides / original_size
        org_total_ratio = (total_org_nucleotides / original_size)/2
        total_ratio = total_ratio
        print(f"Total Ratio of Nucleotides to Original Text File Size: {total_ratio:.6f}")
        if not args.noindels:
            relative_ratio = (abs(total_ratio - org_total_ratio)/org_total_ratio) * 100
            print(f"Relative Ratio of Nucleotides to Original Text File Size: {relative_ratio:.6f}")
    else:
        print("Original text file size is zero, cannot calculate ratio.")

if __name__ == "__main__":
    main()
