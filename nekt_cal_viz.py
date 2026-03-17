import echopype as ep
import xarray as xr
import matplotlib.pyplot as plt
import glob
import os
import warnings

# Use specific warnings filter to keep output clean
warnings.filterwarnings('ignore')

# --- USER CONFIGURATION ---
# Define the path to your folder containing the .nc files
data_dir = 'data_processed/202305_nc'  # Change this to your actual directory path
mooring_depth = 159 
mooring_pressure = mooring_depth * 1.01
bad_line_min = 97 
bad_line_max = 102

# Define your pattern here. 
file_pattern = input("Enter the file pattern (e.g., '230402*.nc'): ")

# --------------------------

# 1. Generate the file list automatically
search_path = os.path.join(data_dir, file_pattern)
file_list = sorted(glob.glob(search_path)) # 'sorted' ensures chronological order

print(f"Found {len(file_list)} files matching pattern: {file_pattern}")

if not file_list:
    print("No files found. Please check your directory and pattern.")
else:
    # 2. Define environment parameters
    env_params = {
        'temperature': 4, 
        'salinity': 35,    
        'pressure': mooring_pressure     
    }

    # 3. Loop, calibrate, and collect
    sv_datasets = []

    print("Processing files and computing Sv...")
    for file in file_list:
        try:
            # Open converted file
            ed = ep.open_converted(file)
            
            # Calibrate to get Sv
            ds_Sv = ep.calibrate.compute_Sv(ed, env_params=env_params)
            
            sv_datasets.append(ds_Sv)
        except Exception as e:
            print(f"Error processing {file}: {e}")

    # 4. Concatenate
    if sv_datasets:
        print("Concatenating datasets...")
        combined_ds = xr.concat(sv_datasets, dim='ping_time')

        print("Combination complete. Total pings:", len(combined_ds.ping_time))

        print("Selecting the channel...")
        # --- Interactive Channel Selection ---

        # 1. Get the list of available channels from the dataset
        available_channels = combined_ds.channel.values

        print("\n--- Available Channels ---")
        # 2. Loop through and print them with a number (1, 2, 3...)
        for index, channel_name in enumerate(available_channels):
            print(f"{index + 1}: {channel_name}")

        # 3. Ask user for input
        try:
            user_input = int(input("Enter the number of the channel you want to plot: "))
    
            # 4. Convert user input (1-based) to list index (0-based)
            selected_index = user_input - 1
    
            # 5. Store the selected channel ID in a variable
            selected_channel_id = available_channels[selected_index]
            print(f"-> Selected Channel: {selected_channel_id}")

        except (ValueError, IndexError):
            print("Invalid selection. Defaulting to the first channel.")
            selected_channel_id = available_channels[0]

        # --- Apply Selection ---

        # 6. Use the variable to select the data
        ds_plot = combined_ds.sel(channel=selected_channel_id)

        # --- NEW STEP: Calculate True Depth & Mask Lines ---
        print("Calculating True Depth and removing interference lines...")

        # A. Calculate Depth: Mooring Depth - Range
        # We assign it as a coordinate so we can plot against it
        if 'echo_range' in ds_plot:
             true_depth = mooring_depth - ds_plot['echo_range']
             ds_plot = ds_plot.assign_coords(depth=true_depth)
        else:
             # Fallback just in case, though compute_Sv usually provides it
             print("Warning: 'echo_range' missing. Plotting might fail.")

        # B. Remove Instrumental Lines (97m - 102m)
        # Logic: Keep data where depth is LESS than 97 OR GREATER than 102
        mask_good_data = (ds_plot['depth'] < bad_line_min) | (ds_plot['depth'] > bad_line_max)
        ds_plot['Sv'] = ds_plot['Sv'].where(mask_good_data)

        # ---------------------------------------------------

        # 6. Plot
        plt.figure(figsize=(15, 6))
        
        # Plotting Sv against 'depth' instead of 'range_sample'
        ds_plot['Sv'].plot(
            x='ping_time', 
            y='depth',       # <--- Changed to depth
            cmap='viridis', 
            vmin=-90, 
            vmax=-40
        )

        # Invert Y-axis: 
        # Since Depth 0 is Surface and Depth 159 is Sensor,
        # Inverting puts 0 (Surface) at the Top.
        plt.gca().invert_yaxis()
        
        plt.title(f"AZFP Echogram - {file_pattern} - Channel: {selected_channel_id}")
        plt.xlabel("Time")
        plt.ylabel("True Depth (m)") # Updated Label
        
        # Add a reference line for the sensor
        plt.axhline(y=mooring_depth, color='red', linestyle='--', label='Sensor Depth')
        plt.legend()

        # Formatting the x-axis to be readable
        plt.gcf().autofmt_xdate()
        
        plt.show()
    else:
        print("No datasets were successfully processed.")