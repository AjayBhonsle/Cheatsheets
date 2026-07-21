import glob
import os
import time
import pandas as pd


def process_all_files(
    input_dir="Python\Interview\LargeFileProcessing\iot_logs", output_file="Python\Interview\LargeFileProcessing\processed_output_seq.csv"
):
    start_time = time.perf_counter()
    file_list = glob.glob(os.path.join(input_dir, "*.csv"))
    all_transformed_rows = []

    # 1. Loop through all files 1-by-1
    for file_path in file_list:
        df_temp = pd.read_csv(file_path)

        # 2. Filter out 'OK' status rows
        df_temp = df_temp[df_temp["status"] != "OK"].copy()

        if not df_temp.empty:
            # 3. Transform: Calculate power_watts
            df_temp["power_watts"] = (
                df_temp["voltage"] * df_temp["current_draw"]
            ).round(2)

            # 4. Add tracking metadata
            df_temp["processed_file"] = os.path.basename(file_path)
            df_temp["processed_by_worker"] = "MainProcess"
            df_temp["load_timestamp"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            all_transformed_rows.append(df_temp)

    # 5. Combine into a single final DataFrame
    if all_transformed_rows:
        final_df = pd.concat(all_transformed_rows, ignore_index=True)

        # Select & order final columns
        final_cols = [
            "timestamp",
            "device_id",
            "status",
            "error_code",
            "power_watts",
            "processed_file",
            "processed_by_worker",
            "load_timestamp"
        ]
        final_df = final_df[final_cols]

        # 6. Load into final CSV
        final_df.to_csv(output_file, index=False)
        print(
            f"Processed {len(file_list)} files into {len(final_df)} rows in {time.perf_counter() - start_time:.2f} seconds."
        )
    else:
        print("No non-OK records found to process.")


if __name__ == "__main__":
    process_all_files()