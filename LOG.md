-------------
# AZFP Project Log: NekTone-Processing-AZFP

This log details the setup, configuration, and daily progress for the research project focusing on acoustic zooplankton fish profiler (AZFP) data from the NL region.

## Things to consider
- Used constant 1.35 for 200ms, 200hz frequency
- Used Temperature 4°C for bottom sensor
- Used salinity 35PPT for now!
- Used 

## 2025-10-21 (Initial Setup Phase)

### ⚙️ Environment Setup and Configuration
| Step | Status | Notes |
| :--- | :--- | :--- |
| **Install Anaconda Distribution** | **COMPLETED** | Downloaded and installed the Anaconda distribution, which includes Anaconda Navigator. |
| **Create Conda Environment** | **COMPLETED** | Created a dedicated Python environment named `azfp` for project isolation. |
| **Install JupyterLab** | **COMPLETED** | Installed the `jupyterlab` package within the `azfp` environment using `conda install jupyterlab`. |
| **Install Echopype** | **COMPLETED** | Installed the core processing library using `pip install echopype` within the `azfp` environment. |
| **GitHub Repository Creation** | **COMPLETED** | Created the repository `NekTone-Processing-AZFP` on GitHub, including a **README.md** and **MIT License**. |

### 🛠️ Git & Local Workspace Configuration

| Step | Status | Notes |
| :--- | :--- | :--- |
| **Local Folder Location** | **COMPLETED** | Set the local workspace to the dedicated path: `D:\Work\NekTone-Processing-AZFP`. |
| **Git Identity Setup** | **SOLVED** | Encountered **"Author identity unknown"** error. Fixed by running `git config --global user.email` and `git config --global user.name` in the Anaconda Prompt. |
| **Initial Git Pull** | **SOLVED** | Encountered "failed to push" error due to remote `README`/`LICENSE` creation. Solved by running `git pull origin main` to merge histories. |
| **Final Git Push** | **SOLVED** | Encountered **`error: src refspec main does not match any`**. Solved by using `git push -u origin main` (or `master`) to explicitly set the upstream branch. |
| **Data Folder Creation** | **COMPLETED** | Created `data_raw/` and `data_processed/` subdirectories for organizational structure. |
| **`LOG.md` Creation & Push** | **COMPLETED** | Created and pushed this file to GitHub for online progress tracking. |

### 🐛 Solved Infrastructure Issues

* **Conda Not Recognized:** Identified that `conda` commands only work outside the standard Windows terminal. Solution is to use the **Anaconda Prompt**.
* **JupyterLab Launch Location:** Identified that JupyterLab was not saving files to the project directory (`D:\Work\...`). Solution is to switch drives (`D:`) and run `cd D:\Work\NekTone-Processing-AZFP` *before* running `jupyter lab`.

---

## 2025-11-06 (Current Status)

### 🟢 Progress Summary (What was accomplished)
* Completed all infrastructure setup (Anaconda, Git, JupyterLab).
* Resolved all initial Git configuration and terminal navigation issues.
* The project is now fully initialized and synchronized between the local D: drive folder and GitHub.

### ➡️ Next Step (The task to start today)
* **CORE HOMEWORK TASK:** Open the JupyterLab notebook (`01_AZFP_Data_Conversion.ipynb`) and run the Echopype script to load **one** raw `.01A` file and convert it to the analysis-ready NetCDF format (`AZFP_202304_converted.nc`).

---

## 2025-11 to 2026-03 (Data Processing & Analysis Phase)

### 📊 Acoustic Data Pipeline & Processing
| Step | Status | Notes |
| :--- | :--- | :--- |
| **Data Conversion & Calibration** | **COMPLETED** | Successfully converted raw files and calibrated to compute $S_v$ using `ep.calibrate.compute_Sv()`. Applied environmental parameters (Temp: 4°C, Salinity: 35, Pressure: 159 * 1.01). |
| **Applying Masks & Filters** | **COMPLETED** | Implemented depth masking to remove surface interference (<0m), bottom artifacts (>157m), and specific hardware interference bands (97m - 102m). |
| **Data Binning (MVBS)** | **COMPLETED** | Calculated Mean Volume Backscattering Strength (MVBS) to condense high-resolution data. Established 1 Hour x 5 Meter resolution as the optimal balance between detail and processing speed. Merged daily data into monthly `.nc` files. |
| **Background Noise Removal** | **TESTED** | Integrated the De Robertis & Higginbottom (2007) algorithm via `ep.clean.remove_background_noise`. |


### 📈 Data Visualization & Biological Metrics
| Step | Status | Notes |
| :--- | :--- | :--- |
| **Frequency Distribution Analysis** | **COMPLETED** | Generated $S_v$ histograms to mathematically separate background noise/empty ocean from the "biological tail." Used this to justify SNR thresholds and identify non-biological anomalies (e.g., sharp spikes at -60 dB). |
| **Center of Mass (CM) Calculation** | **COMPLETED** | Developed script to calculate the depth-weighted Center of Mass based on Urmy et al. (2012) to track Diurnal Vertical Migration (DVM). Handled conversion from logarithmic $S_v$ to linear $s_v$ for accurate mathematical weighting. |
| **Timezone Alignment** | **CONSIDERED/Not Applied Yet** | Identified the "DVM Trap" (AZFP records in UTC). Verified the mathematical alignment of the dawn descent with local Newfoundland Daylight Time (UTC-2.5) sunrise. |
| **Custom Visualization Tool** | **COMPLETED** | Built an automated, terminal-based Python script to instantly slice data by date/channel and generate high-resolution DVM tracking plots without loading massive datasets into memory. |

### 🐛 Solved Methodological & Code Issues
* **`echo_range` vs `depth` Conflict:** Discovered that running background noise removal on `depth` destroys the spherical spreading physics. Solved by patching `sound_absorption` from raw files into the binned files, manipulating `xarray` dimensions (renaming `echo_range` to `range_sample`), and correctly applying the TVG compensation.
* **Binning Artifacts:** Realized that binning *before* noise removal artificially raises the noise floor. Successfully implemented a temporary 10dB SNR threshold for progress visualizations, need to remove the noise floor again before binning, with the permanent fix documented to move noise removal inside the pre-binning loop (at 3dB SNR) for the final thesis pipeline. Need to finalise the outline and details first

### 🟢 Progress Summary (March 2026)
* The core acoustic processing pipeline is functional from raw conversion to final biological visualization.
* Successfully extracted and plotted a textbook Diurnal Vertical Migration (DVM) "heartbeat" from the May 2023 125 kHz dataset.

### ➡️ Next Steps
* Move the Higginbottom background noise removal step *inside* the main processing loop (before binning) using a 3dB threshold for final, rigorous thesis data products.
* Calculate **Inertia (Variance)** alongside the Center of Mass to quantify the thickness and dispersion of the zooplankton scattering layers.
* Begin integrating in-situ data for environmental correlation.
