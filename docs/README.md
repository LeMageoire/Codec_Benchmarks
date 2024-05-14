# Design of the benchmarks

- should print the start time and stop time 
- for every step of the program

- 


- benchmarks_config is a json file :
    - "name"
    - "args"
        - error_rate
        - package_redundancy   

```python
import subprocess

def run_program_with_timeout(command, timeout):
    try:
        # Run the command as a subprocess and wait for the specified timeout
        result = subprocess.run(command, timeout=timeout, text=True, capture_output=True)
        return result.stdout  # Return the standard output of the subprocess
    except subprocess.TimeoutExpired:
        print("The process timed out. Terminating...")
        return "Timeout"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error"

# Example usage
command = ['path/to/your/executable']  # Replace with the actual command to run your program
timeout_seconds = 60  # Set the timeout duration in seconds
output = run_program_with_timeout(command, timeout_seconds)
print(output)
```