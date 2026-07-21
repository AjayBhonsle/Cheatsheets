import csv
import glob
import multiprocessing
import os
import time
import pandas as pd
from concurrent.futures import ProcessPoolExecutor


def process_single_file(file_path):
    """Worker function: Executed in parallel by separate CPU process workers.

    Reads, filters, and transforms a single CSV file line-by-line.
    """
    # Identify which worker process is executing this task
    worker_name = multiprocessing.current_process().name

    transformed_rows = []

    # Stream file line-by-line using DictReader for low memory footprint
    with open(file_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            # Step 1: Clean/Filter - Ignore 'OK' status rows
            if row["status"] == "OK":
                continue

            # Step 2: Transform - Compute power in Watts (Voltage * Current)
            power_watts = round(float(row["voltage"]) * float(row["current_draw"]), 2)

            load_timestamp = (
                pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                if "pd" in globals()
                else time.strftime("%Y-%m-%d %H:%M:%S.")
                + f"{int((time.time() % 1) * 1000):03d}"
            )

            # Step 3: Append processed row along with worker tracking metadata
            transformed_rows.append(
                [
                    row["timestamp"],
                    row["device_id"],
                    row["status"],
                    row["error_code"],
                    power_watts,
                    os.path.basename(file_path),  # File name processed
                    worker_name,  # Worker process identity
                    load_timestamp,
                ]
            )

    return transformed_rows


def process_all_files(input_dir="Python\Interview\LargeFileProcessing\iot_logs", output_file="Python\Interview\LargeFileProcessing\processed_output.csv"):
    start_time = time.perf_counter()  # Start timer

    # Fetch all CSV paths from source directory
    file_list = glob.glob(os.path.join(input_dir, "*.csv"))

    # Define headers including tracking columns
    output_headers = [
        "timestamp",
        "device_id",
        "status",
        "error_code",
        "power_watts",
        "processed_file",
        "processed_by_worker",
        "load_timestamp"
    ]

    # Open single target file for aggregated streaming output
    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(output_headers)  # Write CSV header row

        # Initialize process pool (defaults to cpu_count worker processes)
        with ProcessPoolExecutor() as executor:
            # Map file_list across parallel worker processes
            for file_results in executor.map(process_single_file, file_list):
                if file_results:
                    # Stream write completed batch directly to disk
                    writer.writerows(file_results)

    end_time = time.perf_counter()  # Stop timer
    print(f"Processed {len(file_list)} files in {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    process_all_files()