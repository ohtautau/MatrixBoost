import subprocess
import csv
import os

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def compile_runfile(source_file, output_directory, compile_options=""):
    create_directory(output_directory)
    executable_path = os.path.join(output_directory, os.path.basename(source_file).replace(".c", ""))

    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Source file {source_file} not found.")

    compile_command = f"gcc {source_file} -o {executable_path} {compile_options}".strip()
    result = subprocess.run(compile_command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Compilation failed for {source_file}:\n{result.stderr}")
    return executable_path

def run_matrix_multiplication(N, method, events, output_directory, source_file, compile_options, core_id=None, runs=3):
    create_directory(output_directory)
    build_directory = "build"
    executable_path = compile_runfile(source_file, build_directory, compile_options)
    method_filename = os.path.join(output_directory, f"{method}_results.csv")

    with open(method_filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Method", "Average Execution Time (s)"] + events)

        exec_times = []
        event_totals = {event: 0 for event in events}

        for run in range(1, runs + 1):
            command = f"./{executable_path} {N}"
            perf_command = (
                f"taskset 0x{1 << core_id:x} perf stat -e {','.join(events)} {command}"
                if core_id is not None and core_id >= 0
                else f"perf stat -e {','.join(events)} {command}"
            )
            print(f"Executing command: {perf_command}")

            result = subprocess.run(perf_command, shell=True, capture_output=True, text=True)
            print(result.stderr)

            output = result.stderr
            exec_time = next(
                (float(line.split()[0]) for line in output.splitlines() if "seconds time elapsed" in line), None
            )
            exec_times.append(exec_time)

            for event in events:
                for line in output.splitlines():
                    if event in line:
                        value = line.split()[0].replace(",", "")
                        event_totals[event] += int(value) if value.isdigit() else 0

        avg_exec_time = sum(exec_times) / len(exec_times)
        event_averages = {event: event_totals[event] / runs for event in events}
        writer.writerow([method, avg_exec_time] + [event_averages[event] for event in events])

def main():
    N = 500 # Matrix size
    runs = 3 # The number of running
    methods = {
        "mat_mul_ikj": {"compile_options": "", "core_id": 0}, # None indicates no use of CPU affinity.
        "mat_mul_ijk": {"compile_options": "", "core_id": 0},
        "mat_mul_kij": {"compile_options": "", "core_id": 0},
        "mat_mul_jik": {"compile_options": "", "core_id": 0},
        "mat_mul_jki": {"compile_options": "", "core_id": 0},
        "mat_mul_kji": {"compile_options": "", "core_id": 0},
        "mat_mul_ijk_simd": {"compile_options": "-mavx2", "core_id": 0},
    }
    output_directory = "metrics"
    source_directory = "src"
    events = ["mem_load_retired.l1_miss", "l2_rqsts.miss", "LLC-load-misses", "cache-misses", 
              "instructions", "branches", "cycles", "context-switches"]

    for method, config in methods.items():
        source_file = os.path.join(source_directory, f"{method}.c")
        try:
            run_matrix_multiplication(
                N, method, events, output_directory, source_file, 
                config["compile_options"], config["core_id"], runs
            )
        except FileNotFoundError as e:
            print(f"Skipping {method}: {e}")
        except RuntimeError as e:
            print(f"Error running {method}: {e}")

if __name__ == "__main__":
    main()
