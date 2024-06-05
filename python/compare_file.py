import argparse

def compare_files(file1, file2, chunk_size=1024):
    """
    Compare two files byte by byte and calculate the percentage of error
    based on the number of differing bytes.
    """
    total_bytes = 0
    mismatched_bytes = 0

    # we have to try catch the fils
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        while True:
            chunk1 = f1.read(chunk_size)
            chunk2 = f2.read(chunk_size)
            # Check if we've reached the end of both files
            if not chunk1 and not chunk2:
                break
            
            # Compare byte by byte
            min_len = min(len(chunk1), len(chunk2))
            total_bytes += min_len
            mismatched_bytes += sum(chunk1[i] != chunk2[i] for i in range(min_len))
            
            # Add the remaining bytes if the chunks are of different lengths
            mismatched_bytes += abs(len(chunk1) - len(chunk2))
            total_bytes += abs(len(chunk1) - len(chunk2))
    
    # If there are no bytes to compare, avoid division by zero
    if total_bytes == 0:
        return 100 if chunk1 != chunk2 else 0
    
    # Calculate percentage of differing bytes
    error_percentage = (mismatched_bytes / total_bytes) * 100
    return error_percentage

def main():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description="Compare two files byte by byte and calculate the percentage of error")
    parser.add_argument('--results', '-r', dest='tocomp', help="Path to the original file")
    parser.add_argument('--inputs', '-i', dest='original', help="Path to the decoded file")
    args = parser.parse_args()
    
    error_percentage = compare_files(args.original, args.tocomp)
    if error_percentage == 0:
        print("The files are identical.")
    else:
        print(f"The files are different. Error percentage: {error_percentage:.2f}%.")

if __name__ == "__main__":
    main()
