# NekTone-Processing-AZFP
Processing the AZFP data from the Labrador Sea to analyse the pattern in zooplankton and nekton behaviours. The research project uses echopype package to process the raw ASL AZFP data. The repository is in the initial phase and will be updated gradually as the project progresses.

# Steps to follow 
To achieve echograms of the water columns from raw data, the following steps need to be done.

### 1. Convert to netCDF
First, the raw .01A files need to be converted to netCDF files using the master XML files generated during deployment. In the current version of the script, it batch processes all the raw files from one deployment and store it into individual netcdf files in a separate output folder. Alternatively, monthly processing is also possible for a specific month.

### 2. Calibrate with Environment Parameters
Temperature, Salinity and Water Pressure is needed to calibrate the netCDF files and generate echograms. The mooring depth of the sensor is needed to convert the range of the sensor to true depth. Any interference noise from internal or external sources needs to be masked.

### 3. Binning for each month
Binning the hourly files into a single netCDF file for a month is needed to easily manage the analysis process and storage. The current script has variable for time and depth resolution which is used for binning. By default, 1 hour * 5 meter resolution is set in the script which can be changed easily. The script takes a file pattern input to easily identify which month needs to be binned. (For example: 1711* can be given as a input to bin files for November 2017) 

### 4. Analyzing the metrices
Center of mass and MVBS will be calculated to analyse the migration pattern of nekton in the water column.
