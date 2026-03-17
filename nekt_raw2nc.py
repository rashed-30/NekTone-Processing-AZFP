# --- CELL 1: Import Libraries ---
# Import echopype for conversion, os/glob/pathlib for finding files, and time for timing the process.
import echopype as ep
import os
import glob
from pathlib import Path
import time
import xarray as xr # We import xarray to show how to open the data at the end

print("Libraries imported successfully.")
# --- CELL 2: Define Your Project Paths ---
# This cell finds all your main data folders.

# This command gets the path to your current project folder (NekTone-Processing-AZFP)
# This works because you launched JupyterLab from this directory!
PROJECT_ROOT = os.getcwd() 
print(f"Project Root: {PROJECT_ROOT}")

# Define the base raw data directory (where the '55139' folder is)
BASE_RAW_PATH = os.path.join(PROJECT_ROOT, "data_raw", "STN27-AZFP-02") # We add "202304" here to point directly to the month folder
print(f"Base Raw Path: {BASE_RAW_PATH}")

# Define the base processed data directory (where the new folders will be created)
BASE_PROCESSED_PATH = os.path.join(PROJECT_ROOT, "data_processed")
print(f"Base Processed Path: {BASE_PROCESSED_PATH}")

# --- CELL 3: List the Months You Want to Process ---

# *** IMPORTANT: EDIT THIS LIST ***
# Add the folder names for the months of data you have.

DATA_TO_PROCESS = [
    '55139' 
]

print(f"Months to process: {DATA_TO_PROCESS}")

# --- CELL 4: The Main Conversion Loop ---
# This script will now loop over each month, find all .01A files,
# convert them, and save them as .nc files in the new folders.

print("\n--- STARTING BATCH CONVERSION ---")
start_time = time.time() # Start a timer

# --- NEW: Find the master XML file ONCE ---
# We assume the XML file is in the '55139' folder (BASE_RAW_PATH)
xml_files_list = glob.glob(os.path.join(BASE_RAW_PATH, "*.XML"))
if not xml_files_list:
    # If no .XML (uppercase) found, try .xml (lowercase)
    xml_files_list = glob.glob(os.path.join(BASE_RAW_PATH, "*.xml"))

if not xml_files_list:
    print(f"  *** CRITICAL ERROR: No .XML or .xml file found in {BASE_RAW_PATH} ***")
    print(f"  Please add Correct Master XML file to that folder and re-run.")
    # We stop the script here because it cannot proceed without this file.
    raise FileNotFoundError("Master XML file not found. Halting conversion.")
    
# Use the first XML file found in the directory
xml_file_path = xml_files_list[0]
print(f"  Using Master XML metadata file: {Path(xml_file_path).name}")
# --- END NEW CODE ---

for month_folder in DATA_TO_PROCESS:
    print(f"\nProcessing Month: {month_folder}")
    
    # 1. Define the input directory for this month's raw files
    input_dir = os.path.join(BASE_RAW_PATH, month_folder)
    
    # 2. Define and create the output directory for this month's .nc files
    output_dir = os.path.join(BASE_PROCESSED_PATH, f"2nd Deployment_ {month_folder}_nc") # e.g., "202304_nc"
    os.makedirs(output_dir, exist_ok=True) # This creates the folder (and does nothing if it already exists)
    print(f"  Output folder ready: {output_dir}")
    
    # 3. Find all raw .01A files in the input directory
    # The '*' is a wildcard that means "match anything"
    raw_files_list = glob.glob(os.path.join(input_dir, "*.01A"))
    print(f"  Found {len(raw_files_list)} raw files to convert.")

    # 4. Loop through each raw file, convert it, and save it
    for raw_file_path in raw_files_list:
        # Get just the filename, e.g., "23040100.01A"
        file_name = Path(raw_file_path).name 
        
        # Create the new output filename, e.g., "23040100.nc"
        output_name = Path(raw_file_path).stem + ".nc" 
        
        # Create the full path for the new file
        output_file_path = os.path.join(output_dir, output_name)
        
        print(f"    Converting: {file_name} -> {output_name}")
        
        try:
            # --- This is the core echopype conversion ---
            # --- MODIFIED LINE: We pass the XML path found *outside* the loop ---
            ed = ep.open_raw(
                raw_file_path, 
                sonar_model='AZFP', 
                xml_path=xml_file_path  # Explicitly tell echopype where the settings are
            )
            
            # --- This saves the converted data to the .nc file ---
            ed.to_netcdf(save_path=output_file_path, overwrite=True)
            
        except Exception as e:
            # If one file fails, this will print the error and continue to the next file
            print(f"      *** ERROR converting {file_name}: {e} ***")
            pass
    
    print(f"  Finished processing all files for {month_folder}.")

end_time = time.time()
print(f"\n--- BATCH CONVERSION COMPLETE ---")
print(f"Total time taken: {end_time - start_time:.2f} seconds")