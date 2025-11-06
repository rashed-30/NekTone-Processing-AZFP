# AZFP Project Log: NekTone-Processing-AZFP

This log details the setup, configuration, and daily progress for the research project focusing on acoustic zooplankton fish profiler (AZFP) data from the NL region.

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