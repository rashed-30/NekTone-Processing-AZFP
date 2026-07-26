import echopype as ep
import xarray as xr
import glob
import os
import warnings
import numpy as np
import gc
from collections import defaultdict

# Adjust imports based on your specific echopype installation/dev branch
from echopype_dev.echopype.clean.api import remove_background_noise

warnings.filterwarnings('ignore')

# --- 1. CONFIGURATION ---
# UPDATE THIS: Point to the folder containing all your 1711...nc files
base_input_folder = 'data_processed/4th Deployment_ 55139_nc' 
output_folder = 'data_products_monthly'

mooring_depth = 160
bad_line_min, bad_line_max = 97, 102
surface_cutoff, bottom_cutoff = 0, 157
res_time, res_depth = "1H", "2m"

# ENvironmental parameters for calibration (if needed)
temp = 4  # degrees Celsius
sal = 32  # PSU

# Standard Scenario Thresholds
thr_impulse = '10.0dB'
m_impulse = '3m'
thr_transient = '12.0dB'
m_transient = '5m'
n_transient = 20
snr_background = '5dB'

# ---------------------------

os.makedirs(output_folder, exist_ok=True) 

# --- 2. FILE GROUPING LOGIC ---
# Get all .nc files in the flat folder
all_files = sorted(glob.glob(os.path.join(base_input_folder, '*.nc')))

# Group files by the first 4 characters (YYMM)
# Example: "17111812.nc" -> key: "1711"
monthly_groups = defaultdict(list)
for f in all_files:
    file_name = os.path.basename(f)
    if len(file_name) >= 4 and file_name[:4].isdigit():
        month_id = file_name[:4] 
        monthly_groups[month_id].append(f)

print(f"Found {len(monthly_groups)} distinct months to process.")

# --- 3. MAIN PROCESSING LOOP ---
for month_id in sorted(monthly_groups.keys()):
    # Convert YYMM to YYYYMM (e.g., 1711 -> 201711)
    full_month_name = f"20{month_id}"
    output_filename = f"{full_month_name}_{res_depth}.nc"
    save_path = os.path.join(output_folder, output_filename)
    
    if os.path.exists(save_path):
        print(f"Skipping {full_month_name}: {output_filename} already exists.")
        continue

    file_list = monthly_groups[month_id]
    print(f"\n{'='*40}\nProcessing Month: {full_month_name} ({len(file_list)} files)\n{'='*40}")

    mvbs_datasets = []

    for i, file in enumerate(file_list):
        try:
            orig_filename = os.path.splitext(os.path.basename(file))[0]
            print(f"[{i+1}/{len(file_list)}] {orig_filename}...", end='\r')
            
            # A. Open & Calibrate
            ed = ep.open_converted(file)
            ds_Sv = ep.calibrate.compute_Sv(ed, env_params={'temperature': temp, 'salinity': sal, 'pressure': mooring_depth * 1.01})

            # B. The "Bucket" Setup
            if 'echo_range' in ds_Sv.coords: ds_Sv = ds_Sv.reset_coords('echo_range')
            if 'depth' in ds_Sv.coords: ds_Sv = ds_Sv.drop_vars('depth')
            ds_Sv = ds_Sv.assign_coords(depth=(mooring_depth - ds_Sv['echo_range']))

            # C. Apply Spatial Masks
            ds_Sv['Sv'] = ds_Sv['Sv'].where(ds_Sv['depth'] > surface_cutoff)
            ds_Sv['Sv'] = ds_Sv['Sv'].where(ds_Sv['depth'] < bottom_cutoff)
            ds_Sv['Sv'] = ds_Sv['Sv'].where((ds_Sv['depth'] < bad_line_min) | (ds_Sv['depth'] > bad_line_max))

            # D. NOISE REMOVAL
            # 1. Impulse
            impulse_mask = ep.clean.mask_impulse_noise(ds_Sv, impulse_noise_threshold=thr_impulse, depth_bin=m_impulse, range_var='echo_range', use_index_binning=True)
            impulse_mask = impulse_mask.transpose(*ds_Sv['Sv'].dims)
            ds_Sv['Sv'] = ds_Sv['Sv'].where(~impulse_mask.fillna(False).astype(bool).values)
            del impulse_mask

            # 2. Transient
            transient_mask = ep.clean.mask_transient_noise(ds_Sv, depth_bin=m_transient, num_side_pings=n_transient, transient_noise_threshold=thr_transient, range_var='echo_range', use_index_binning=True)
            transient_mask = transient_mask.transpose(*ds_Sv['Sv'].dims)
            ds_Sv['Sv'] = ds_Sv['Sv'].where(~transient_mask.fillna(False).astype(bool).values)
            del transient_mask

            # 3. Background (Quarantine Method)
            ds_temp = xr.Dataset({'Sv': ds_Sv['Sv']}).assign_coords(echo_range=ds_Sv['echo_range'])
            if 'sound_absorption' in ds_Sv.variables: ds_temp['sound_absorption'] = ds_Sv['sound_absorption']
            freqs = [float(str(ch).split('-')[1]) * 1000 for ch in ds_temp.channel.values]
            ds_temp = ds_temp.assign_coords(frequency_nominal=('channel', freqs))
            
            ds_clean = remove_background_noise(ds_temp, range_sample_num=5, ping_num=3, SNR_threshold=snr_background)
            clean_var = 'Sv_corrected' if 'Sv_corrected' in ds_clean else 'Sv_clean'
            ds_Sv['Sv'].values = ds_clean[clean_var].transpose(*ds_Sv['Sv'].dims).values
            del ds_temp, ds_clean

            # E. BINNING
            ds_mvbs = ep.commongrid.compute_MVBS(ds_Sv, range_var='depth', range_bin=res_depth, ping_time_bin=res_time)
            mvbs_datasets.append(ds_mvbs)
            
            # F. RAM CLEANUP
            ds_Sv.close() 
            del ed, ds_Sv
            gc.collect()

        except Exception as e:
            print(f"\nError on {os.path.basename(file)}: {e}")
            if 'ed' in locals(): del ed
            continue

    # G. CONCATENATE & SAVE
    if mvbs_datasets:
        ds_monthly = xr.concat(mvbs_datasets, dim='ping_time')
        ds_monthly.to_netcdf(save_path)
        print(f"\nSUCCESS: {output_filename} saved.")
        ds_monthly.close()
        for ds in mvbs_datasets: ds.close()
    else:
        print(f"\nNo data processed for {full_month_name}.")

print("\nAll months processed successfully!")