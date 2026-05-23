import json
import sqlite3
import pandas as pd
from pathlib import Path

# ==============================================================================
# PANDAS-ONLY READ/WRITE SYSTEM MASTER CHEAT SHEET
# ==============================================================================

print("==============================================================================")
print("0. SETUP STAGING WORKSPACE")
print("==============================================================================")

STAGE_DIR = Path("./pandas_exclusive_stage")
STAGE_DIR.mkdir(parents=True, exist_ok=True)

# Main test dataset containing strings, integers, and floats
df_test = pd.DataFrame({
    "product_id": [101, 102, 103],
    "category": ["Electronics", "Office Supply", "Furniture"],
    "unit_price": [299.99, 45.50, 120.00]
})

print("Baseline DataFrame to be processed:")
print(df_test)


print("\n==============================================================================")
print("1. COMMA SEPARATED VALUES (.CSV)")
print("==============================================================================")
csv_path = STAGE_DIR / "data_store.csv"

# --- WRITE WAYS ---
# Way A: Standard write without exporting the row indexes
df_test.to_csv(csv_path, index=False)

# Way B: Append new rows directly to the bottom of the existing CSV file
df_append_csv = pd.DataFrame({"product_id": [104], "category": ["Toys"], "unit_price": [15.75]})
df_append_csv.to_csv(csv_path, mode="a", header=False, index=False)

# --- READ WAYS ---
print("Way A (Standard full-file loading):")
df_csv_full = pd.read_csv(csv_path)
print(df_csv_full)

print("\nWay B (Optimized parsing - read only a subset of columns):")
df_csv_cols = pd.read_csv(csv_path, usecols=["product_id", "unit_price"])
print(df_csv_cols)


print("\n==============================================================================")
print("2. JAVASCRIPT OBJECT NOTATION (.JSON)")
print("==============================================================================")
json_path = STAGE_DIR / "data_store.json"

# --- WRITE WAYS ---
# Way A: Records mapping (An array of row-level key-value objects)
df_test.to_json(json_path, orient="records", indent=4)

# Way B: Columns mapping (Grouped entirely by column names)
json_col_path = STAGE_DIR / "data_store_cols.json"
df_test.to_json(json_col_path, orient="columns", indent=4)

# --- READ WAYS ---
print("Way A (Load from records structure layout):")
df_json_rec = pd.read_json(json_path, orient="records")
print(df_json_rec)

print("\nWay B (Load from columns structure layout):")
df_json_col = pd.read_json(json_col_path, orient="columns")
print(df_json_col)


print("\n==============================================================================")
print("3. EXCEL WORKBOOKS (.XLSX)")
print("==============================================================================")
excel_path = STAGE_DIR / "data_store.xlsx"

# --- WRITE WAYS ---
# Way A: Standard single-sheet report creation
df_test.to_excel(excel_path, sheet_name="Current_Inventory", index=False)

# Way B: Write multiple sheets inside the same workbook file using ExcelWriter
with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    df_test.to_excel(writer, sheet_name="Active_Data", index=False)
    df_append_csv.to_excel(writer, sheet_name="Delta_Data", index=False)

# --- READ WAYS ---
print("Way A (Load specific sheet by name):")
df_xl_active = pd.read_excel(excel_path, sheet_name="Active_Data")
print(df_xl_active)

print("\nWay B (Load all sheets at once - returns a dictionary of DataFrames):")
xl_sheets_dict = pd.read_excel(excel_path, sheet_name=None)
print(f" -> Available sheets found: {list(xl_sheets_dict.keys())}")


print("\n==============================================================================")
print("4. APACHE PARQUET (.PARQUET)")
print("==============================================================================")
parquet_path = STAGE_DIR / "data_store.parquet"

# --- WRITE WAYS ---
# Way A: Columnar binary storage using standard Snappy compression
df_test.to_parquet(parquet_path, engine="pyarrow", compression="snappy")

# Way B: Columnar binary storage using Gzip compression layout
parquet_gz_path = STAGE_DIR / "data_store_gzip.parquet"
df_test.to_parquet(parquet_gz_path, engine="pyarrow", compression="gzip")

# --- READ WAYS ---
print("Way A (Standard high-performance binary extraction):")
df_pq_full = pd.read_parquet(parquet_path, engine="pyarrow")
print(df_pq_full)

print("\nWay B (Selective memory optimization - pull only explicit columns):")
df_pq_partial = pd.read_parquet(parquet_path, columns=["category", "unit_price"])
print(df_pq_partial)


print("\n==============================================================================")
print("5. EXTENSIBLE MARKUP LANGUAGE (.XML)")
print("==============================================================================")
xml_path = STAGE_DIR / "data_store.xml"

# --- WRITE WAYS ---
# Way A: Flat standard tag element tree output
df_test.to_xml(xml_path, index=False)

# Way B: Custom hierarchical structure tag names
xml_custom_path = STAGE_DIR / "data_store_custom.xml"
df_test.to_xml(xml_custom_path, root_name="Catalog", row_name="Item", index=False)

# --- READ WAYS ---
print("Way A (Standard markup tree parsing):")
df_xml_standard = pd.read_xml(xml_path)
print(df_xml_standard)

print("\nWay B (Reading custom root/row structures):")
df_xml_custom = pd.read_xml(xml_custom_path)
print(df_xml_custom)

#-------
xml_path = STAGE_DIR / "raw_data.xml"
df_test.to_xml(xml_path, index=False)

# Show what XML looks like on disk
print("--- RAW CONTENT ON DISK (<> Tags) ---")
print(xml_path.read_text().strip())

# Read back into the common grid
print("\n--- HOW PANDAS SEES IT (DataFrame) ---")
print(pd.read_xml(xml_path))


print("\n==============================================================================")
print("6. HIGH-SPEED APACHE ARROW FEATHER (.FEATHER)")
print("==============================================================================")
feather_path = STAGE_DIR / "data_store.feather"

# --- WRITE WAYS ---
# Way A: Fast memory-to-disk binary dump (Optimized for quick processing stages)
df_test.to_feather(feather_path)

# --- READ WAYS ---
print("Way A (Direct Arrow binary restoration stream):")
df_feather = pd.read_feather(feather_path)
print(df_feather)


print("\n==============================================================================")
print("7. HYPERTEXT MARKUP LANGUAGE TABLES (.HTML)")
print("==============================================================================")
html_path = STAGE_DIR / "data_store.html"

# --- WRITE WAYS ---
# Way A: Export directly to a clean HTML static tabular layout string
df_test.to_html(html_path, index=False)

# --- READ WAYS ---
print("Way A (Scrape all table matrices out of an HTML structure file):")
html_tables = pd.read_html(html_path)
df_html = html_tables[0]  # Extracts the first matching matrix found
print(df_html)


print("\n==============================================================================")
print("8. HDF5 HIERARCHICAL STORAGE CORES (.H5)")
print("==============================================================================")
hdf_path = STAGE_DIR / "data_store.h5"

# --- WRITE WAYS ---
# Way A: Serialize data under a specific internal workspace directory path key
df_test.to_hdf(hdf_path, key="reporting/stage_metrics", mode="w")

# --- READ WAYS ---
print("Way A (Target direct processing key path inside the HDF5 archive container):")
df_hdf = pd.read_hdf(hdf_path, key="reporting/stage_metrics")
print(df_hdf)


# Cleanup staging workspace tree
#import shutil
#shutil.rmtree(STAGE_DIR)
print("\n==============================================================================")
print("ALL PANDAS-EXCLUSIVE FORMAT USE CASES EXECUTED CLEANLY")
print("==============================================================================")
