import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import gc

# --- Configuration ---
folder_path = 'data_products_monthly/2m'
bio_threshold = -80  # Sv threshold for biology
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Get file list
files = sorted(glob.glob(os.path.join(folder_path, '*_2m.nc')))

# Automatically learn the 4 available channels from the first file
if files:
    temp_ds = xr.open_dataset(files[0])
    # Assuming 'channel' is the dimension name
    all_channels = temp_ds.channel.values.tolist()
    temp_ds.close()
    print(f"Found {len(files)} files and {len(all_channels)} channels to process:")
    for ch in all_channels: print(f" - {ch}")
else:
    print("❌ No .nc files found.")

metrics_list = []

print("Starting multi-channel metric calculation. This will take a moment...")

for i, file in enumerate(files):
    filename = os.path.basename(file)
    year_month = filename.split('_')[0]
    year, month = int(year_month[:4]), int(year_month[4:])
    
    ds = xr.open_dataset(file)
    # We load sound_absorption to speed up processing of the sub-channels
    if 'sound_absorption' in ds: ds = ds.load() 
    
    # --- INNER LOOP: Iterate over all channels in this file ---
    for channel in all_channels:
        if channel not in ds.channel:
            # Skip if a channel is mysteriously missing (rare for AZFP)
            continue
            
        ds_ch = ds['Sv'].sel(channel=channel)
        sv_linear = 10 ** (ds_ch / 10)
        
        # --- 1. Occupied Area % ---
        occ_pct = (ds_ch > bio_threshold).sum().item() / ds_ch.size * 100
        
        # --- 2. Mean Sa (Biomass) with Zero-Clip ---
        mean_linear = (sv_linear.sum(dim='depth', skipna=True) * 2).mean(dim='ping_time', skipna=True).item()
        
        if mean_linear > 0:
            sa_db = 10 * np.log10(mean_linear)
        else:
            sa_db = -100.0  # Set empty months to -100 dB baseline
        
        # --- 3. Center of Mass (Mean Bio-Depth) ---
        depth_weights = ds_ch.depth
        weighted_depth_array = (sv_linear * depth_weights).sum(dim='depth') / sv_linear.sum(dim='depth')
        mean_depth = weighted_depth_array.mean(dim='ping_time', skipna=True).item()

        # Append comprehensive row (includes Channel)
        # float() wrapping is mandatory for Seaborn stability
        metrics_list.append({
            'Year': year, 
            'Month': month, 
            'Month Name': month_names[month-1],
            'Channel': channel, 
            'Occupied Area (%)': float(occ_pct), 
            'Mean Sa (dB)': float(sa_db), 
            'Center of Mass (m)': float(mean_depth)
        })
    
    # Clean up RAM after each file
    ds.close()
    gc.collect() 
    print(f"[{i+1}/{len(files)}] {year_month} processed.", end='\r')

# Convert the massive list to the new Long format DataFrame
df_metrics_long = pd.DataFrame(metrics_list)
print("\nMulti-channel metric calculation complete! df_metrics_long is ready.")