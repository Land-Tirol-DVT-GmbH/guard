import os
import sys
import time
import subprocess
import psutil
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def run_benchmark(threads, output_dir):
    """
    Run guard_cli.py with specified number of threads and measure performance

    Args:
        threads (int): Number of threads to use
        output_dir (Path): Directory to save output files

    Returns:
        dict: Performance metrics including execution time and memory usage
    """
    # Create output directory if it doesn't exist
    output_path = output_dir / f"output_threads_{threads}"
    output_path.mkdir(parents=True, exist_ok=True)

    # Get list of input files
    input_dir = Path("docs/inputfiles")
    input_files = list(input_dir.glob("*.pdf"))
    total_input_size = sum(f.stat().st_size for f in input_files) / (1024 * 1024)  # MB

    # Command to run guard_cli.py
    cmd = [
        sys.executable,
        "processing/guard_cli.py",
        "-d", "docs/inputfiles",
        "-t", str(threads),
        "-o", str(output_path)
    ]

    # Measure execution time
    start_time = time.time()

    # Run the command and monitor memory usage
    print(f"Running benchmark with {threads} threads...")
    max_memory_used = 0
    memory_samples = []
    cpu_samples = []

    # Start the process
    process = subprocess.Popen(cmd)

    # Monitor memory and CPU usage while the process is running
    while process.poll() is None:
        try:
            # Get the process object for the subprocess
            p = psutil.Process(process.pid)

            # Get memory for the process and all its children
            current_memory = p.memory_info().rss
            current_cpu = p.cpu_percent()

            for child in p.children(recursive=True):
                try:
                    current_memory += child.memory_info().rss
                    current_cpu += child.cpu_percent()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Convert to MB and update max if needed
            current_memory_mb = current_memory / 1024 / 1024
            max_memory_used = max(max_memory_used, current_memory_mb)

            # Store samples for analysis
            memory_samples.append(current_memory_mb)
            cpu_samples.append(current_cpu)

            # Sleep briefly to reduce CPU usage of monitoring
            time.sleep(0.1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process might have terminated between polls
            pass

    # Make sure the process completed successfully
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)

    # Calculate execution time
    execution_time = time.time() - start_time

    # Count processed files and get their sizes
    processed_files = list(output_path.glob('*'))
    total_output_size = sum(f.stat().st_size for f in processed_files) / (1024 * 1024)  # MB

    # Calculate average and peak memory/CPU usage
    avg_memory = sum(memory_samples) / len(memory_samples) if memory_samples else 0
    avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
    peak_cpu = max(cpu_samples) if cpu_samples else 0

    # Calculate throughput (MB/s)
    throughput = total_input_size / execution_time if execution_time > 0 else 0

    # Calculate files per second
    files_per_second = len(input_files) / execution_time if execution_time > 0 else 0

    return {
        "threads": threads,
        "execution_time": execution_time,
        "memory_used_mb": max_memory_used,
        "avg_memory_mb": avg_memory,
        "peak_cpu_percent": peak_cpu,
        "avg_cpu_percent": avg_cpu,
        "processed_files": len(processed_files),
        "input_size_mb": total_input_size,
        "output_size_mb": total_output_size,
        "throughput_mb_per_sec": throughput,
        "files_per_second": files_per_second
    }

def plot_results(results):
    """
    Create plots to visualize benchmark results

    Args:
        results (list): List of dictionaries containing benchmark results
    """
    df = pd.DataFrame(results)

    # Create a figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    # Plot execution time
    axes[0, 0].bar(df['threads'].astype(str), df['execution_time'], color='blue')
    axes[0, 0].set_xlabel('Number of Threads')
    axes[0, 0].set_ylabel('Execution Time (seconds)')
    axes[0, 0].set_title('Execution Time by Thread Count')

    # Plot memory usage (peak and average)
    x = range(len(df['threads']))
    width = 0.35
    axes[0, 1].bar([i - width/2 for i in x], df['memory_used_mb'], width, color='green', label='Peak Memory')
    axes[0, 1].bar([i + width/2 for i in x], df['avg_memory_mb'], width, color='lightgreen', label='Avg Memory')
    axes[0, 1].set_xlabel('Number of Threads')
    axes[0, 1].set_ylabel('Memory Usage (MB)')
    axes[0, 1].set_title('Memory Usage by Thread Count')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(df['threads'].astype(str))
    axes[0, 1].legend()

    # Plot CPU usage
    axes[1, 0].bar([i - width/2 for i in x], df['peak_cpu_percent'], width, color='red', label='Peak CPU')
    axes[1, 0].bar([i + width/2 for i in x], df['avg_cpu_percent'], width, color='lightcoral', label='Avg CPU')
    axes[1, 0].set_xlabel('Number of Threads')
    axes[1, 0].set_ylabel('CPU Usage (%)')
    axes[1, 0].set_title('CPU Usage by Thread Count')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(df['threads'].astype(str))
    axes[1, 0].legend()

    # Plot throughput
    axes[1, 1].bar([i - width/2 for i in x], df['throughput_mb_per_sec'], width, color='purple', label='MB/s')
    axes[1, 1].bar([i + width/2 for i in x], df['files_per_second'], width, color='mediumpurple', label='Files/s')
    axes[1, 1].set_xlabel('Number of Threads')
    axes[1, 1].set_ylabel('Throughput')
    axes[1, 1].set_title('Processing Throughput by Thread Count')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(df['threads'].astype(str))
    axes[1, 1].legend()

    plt.tight_layout()
    plt.savefig('benchmark_results.png')
    print(f"Benchmark visualization saved to benchmark_results.png")

def main():
    # Create output directory
    output_dir = Path("benchmark_results")
    output_dir.mkdir(exist_ok=True)

    # Run benchmarks with 1 and 8 threads
    results = []

    # Run with 1 thread
    print("\n" + "="*80)
    print("Starting benchmark with 1 thread")
    print("="*80)
    results.append(run_benchmark(1, output_dir))

    # Run with 8 threads
    print("\n" + "="*80)
    print("Starting benchmark with 8 threads")
    print("="*80)
    results.append(run_benchmark(8, output_dir))

    # Display basic results
    print("\n" + "="*80)
    print("BENCHMARK SUMMARY")
    print("="*80)

    # Create a DataFrame for easier comparison
    df = pd.DataFrame(results)

    # Basic performance metrics
    print("\nBasic Performance Metrics:")
    print("-" * 80)
    headers = ["Threads", "Execution Time (s)", "Peak Memory (MB)", "Avg Memory (MB)", "Files Processed"]
    print(f"{headers[0]:<10} {headers[1]:<20} {headers[2]:<20} {headers[3]:<20} {headers[4]:<15}")
    print("-" * 80)

    for _, row in df.iterrows():
        print(f"{row['threads']:<10} {row['execution_time']:<20.2f} {row['memory_used_mb']:<20.2f} "
              f"{row['avg_memory_mb']:<20.2f} {row['processed_files']:<15}")

    # CPU usage metrics
    print("\nCPU Usage Metrics:")
    print("-" * 80)
    headers = ["Threads", "Peak CPU (%)", "Avg CPU (%)"]
    print(f"{headers[0]:<10} {headers[1]:<15} {headers[2]:<15}")
    print("-" * 80)

    for _, row in df.iterrows():
        print(f"{row['threads']:<10} {row['peak_cpu_percent']:<15.2f} {row['avg_cpu_percent']:<15.2f}")

    # Throughput metrics
    print("\nThroughput Metrics:")
    print("-" * 80)
    headers = ["Threads", "MB/s", "Files/s", "Input Size (MB)", "Output Size (MB)"]
    print(f"{headers[0]:<10} {headers[1]:<15} {headers[2]:<15} {headers[3]:<20} {headers[4]:<20}")
    print("-" * 80)

    for _, row in df.iterrows():
        print(f"{row['threads']:<10} {row['throughput_mb_per_sec']:<15.2f} {row['files_per_second']:<15.2f} "
              f"{row['input_size_mb']:<20.2f} {row['output_size_mb']:<20.2f}")

    # Calculate performance improvements
    if len(results) >= 2:
        time_speedup = results[0]['execution_time'] / results[1]['execution_time']
        throughput_improvement = results[1]['throughput_mb_per_sec'] / results[0]['throughput_mb_per_sec']
        memory_increase = results[1]['memory_used_mb'] / results[0]['memory_used_mb']

        print("\nPerformance Comparison (1 thread vs 8 threads):")
        print("-" * 80)
        print(f"Time Speedup:           {time_speedup:.2f}x faster with 8 threads")
        print(f"Throughput Improvement: {throughput_improvement:.2f}x higher with 8 threads")
        print(f"Memory Usage Ratio:     {memory_increase:.2f}x more memory with 8 threads")

    # Create visualization
    try:
        plot_results(results)
    except ImportError:
        print("Pandas or Matplotlib not available. Skipping visualization.")

    # Save results to CSV
    try:
        df.to_csv('benchmark_results.csv', index=False)
        print("Benchmark results saved to benchmark_results.csv")
    except ImportError:
        print("Pandas not available. Results not saved to CSV.")

    print("\nBenchmark completed successfully!")

if __name__ == "__main__":
    main()
