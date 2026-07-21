import csv
import os
import random
from datetime import datetime, timedelta


def generate_iot_logs(num_files=1000, rows_per_file=100, output_dir="Python\Interview\LargeFileProcessing\iot_logs"):
    os.makedirs(output_dir, exist_ok=True)

    # Expanded to 10 distinct columns
    headers = [
        "timestamp",
        "device_id",
        "firmware_version",
        "temperature",
        "humidity",
        "voltage",
        "current_draw",
        "signal_strength",
        "error_code",
        "status",
    ]

    devices = [f"DEV-{i:03d}" for i in range(1, 21)]
    firmwares = ["v1.0.2", "v1.1.0", "v2.0.1"]
    statuses = ["OK", "WARN", "ERROR", "CRITICAL"]
    error_codes = ["E00", "E101", "E202", "E404", "E500"]

    start_time = datetime.now()

    for i in range(1, num_files + 1):
        filename = os.path.join(output_dir, f"log_{i:04d}.csv")
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for row_idx in range(rows_per_file):
                # Increment timestamp slightly for each row to simulate actual streaming
                current_time = start_time + timedelta(seconds=row_idx)

                row = [
                    current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    random.choice(devices),
                    random.choice(firmwares),
                    round(random.uniform(15.0, 95.0), 2),  # temp in C
                    round(random.uniform(30.0, 90.0), 2),  # humidity %
                    round(random.uniform(3.1, 5.0), 2),  # voltage
                    round(random.uniform(0.1, 2.5), 2),  # current in A
                    random.randint(-100, -30),  # RSSI signal dBm
                    random.choice(error_codes),
                    random.choice(statuses),
                ]
                writer.writerow(row)


# Execute: Generates 1000 files with 10 columns and 100 rows each
generate_iot_logs(num_files=1000, rows_per_file=100)