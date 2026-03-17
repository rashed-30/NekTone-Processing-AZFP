import xarray as xr
import matplotlib.pyplot as plt
import glob
import os
import warnings
import ipywidgets as widgets
from IPython.display import display, clear_output

# Suppress warnings
warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
input_folder = 'data_products_monthly'  # Where you saved the monthly file
file_pattern = '*.nc'                   # Finds any .nc file

# 1. Find Files
search_path = os.path.join(input_folder, file_pattern)
file_list = sorted(glob.glob(search_path))
file_names = [os.path.basename(f) for f in file_list]

if not file_list:
    print(f"No files found in {input_folder}")
else:
    # --- WIDGET DEFINITIONS ---
    
    # Dropdown for Files
    file_dropdown = widgets.Dropdown(
        options=file_names,
        value=file_names[0],
        description='Month:',
        style={'description_width': 'initial'}
    )

    # Dropdown for Channels (Initially empty, populated dynamically)
    channel_dropdown = widgets.Dropdown(
        options=[],
        description='Channel:',
        disabled=False,
        style={'description_width': 'initial'}
    )

    # Button to trigger plotting
    plot_button = widgets.Button(
        description='Plot Echogram',
        button_style='primary', # 'success', 'info', 'warning', 'danger' or ''
        icon='chart-line'
    )

    # Output area where the plot will appear
    output_plot = widgets.Output()

    # --- LOGIC FUNCTIONS ---

    def get_full_path(filename):
        return os.path.join(input_folder, filename)

    def update_channels(*args):
        """Opens the selected file and updates the channel dropdown options."""
        current_file = get_full_path(file_dropdown.value)
        try:
            with xr.open_dataset(current_file) as ds:
                channels = list(ds.channel.values)
                channel_dropdown.options = channels
                channel_dropdown.value = channels[0] # Default to first channel
        except Exception as e:
            channel_dropdown.options = ['Error reading file']
            print(f"Error: {e}")

    def on_plot_click(b):
        """The main function that runs when you click 'Plot'."""
        with output_plot:
            clear_output(wait=True) # Clear previous plot
            
            target_file = get_full_path(file_dropdown.value)
            selected_channel = channel_dropdown.value
            
            print(f"Plotting {selected_channel} from {os.path.basename(target_file)}...")
            
            try:
                # Open Data
                ds = xr.open_dataset(target_file)
                ds_plot = ds.sel(channel=selected_channel)

                # Determine Y-Axis (Depth vs Range)
                if 'depth' in ds_plot.coords:
                    y_axis = 'depth'
                    y_label = "True Depth (m)"
                elif 'echo_range' in ds_plot.coords:
                    y_axis = 'echo_range'
                    y_label = "Range (m)"
                else:
                    print("Error: No depth or range coordinate found.")
                    return

                # PLOTTING
                plt.figure(figsize=(15, 8))
                
                ds_plot['Sv'].plot(
                    x='ping_time',
                    y=y_axis,
                    cmap='viridis',
                    vmin=-90,
                    vmax=-40  
                )

                plt.gca().invert_yaxis()
                plt.title(f"Monthly Echogram: {os.path.basename(target_file)}\nChannel: {selected_channel} | Resolution: 1H x 1m")
                plt.ylabel(y_label)
                plt.xlabel("Date")
                plt.gcf().autofmt_xdate()
                plt.show()

                # Print Stats
                print(f"Date Range: {ds_plot.ping_time.min().values} to {ds_plot.ping_time.max().values}")
                print(f"Depth Range: {ds_plot[y_axis].min().values:.1f}m to {ds_plot[y_axis].max().values:.1f}m")
                
            except Exception as e:
                print(f"Error plotting: {e}")

    # --- CONNECT WIDGETS ---
    
    # When file changes, run update_channels
    file_dropdown.observe(update_channels, names='value')
    
    # When button clicks, run plotting
    plot_button.on_click(on_plot_click)

    # Initialize channels for the first file in the list
    update_channels()

    # --- DISPLAY ---
    # Create a nice layout
    ui = widgets.VBox([
        widgets.HBox([file_dropdown, channel_dropdown]),
        plot_button,
        output_plot
    ])
    
    display(ui)