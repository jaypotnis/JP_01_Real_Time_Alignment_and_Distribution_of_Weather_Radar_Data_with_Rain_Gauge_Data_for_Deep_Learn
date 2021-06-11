import requests
import pandas as pd
import numpy as np
import pyart
import os
import six
import nexradaws
from datetime import datetime
import shutil
import matplotlib.pyplot as plt
import geopy.distance
import pickle
import datetime as dt
import numpy.ma as ma
import time
import warnings
warnings.filterwarnings('ignore')

# recreate folders to ensure that we do not have old files in our folders
def recreate_folder(folder):
    shutil.rmtree(folder, ignore_errors=True)
    os.mkdir(folder)
    
# Function to replace the nan values in reflectivity to -9999
def replace_if_nan(reflectivity_value):
    if (reflectivity_value == '--'):
        corrected_reflectivity = -9999
    else:
        corrected_reflectivity = reflectivity_value
    return corrected_reflectivity

# This function downloads WSR-88D radar data
def download_radar_data(download_folder, unzipped_data_folder, scan):
    # Download a file
    conn = nexradaws.NexradAwsInterface()
    localfiles = conn.download(scan, download_folder)
    radar_filename = sorted(os.listdir(download_folder))[0]
    radar_filepath = download_folder + radar_filename
    # Remove MDM files as we do not need them
    if '_MDM' in radar_filename:
        os.remove(radar_filepath)
    else:
        # Unzip downloaded data if it is zipped
        if (radar_filename[-3:] == '.gz'):
            with gzip.open(radar_filepath, 'rb') as f_in:
                with open(unzipped_data_folder + radar_filename[:-3], 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            radar_filename = radar_filename[:-3]
        else:
            shutil.move(radar_filepath, unzipped_data_folder + radar_filename)
    return radar_filename


# This function grids the WSR-88D data using pyart
def grid_data(unzipped_data_folder, gridded_data_folder, radar_filename):
    grid_x, grid_y, grid_z = 160, 160, 4
    grid_range_x, grid_range_y, grid_range_z = (-100000., 100000), (-100000., 100000.), (1500., 4500.)
    radar = pyart.io.read_nexrad_archive(unzipped_data_folder + radar_filename)
    grid = pyart.map.grid_from_radars(radar,
                                    grid_shape = (grid_z, grid_x, grid_y),
                                    grid_limits = (grid_range_z, grid_range_x, grid_range_z,),
                                    gridding_algo='map_gates_to_grid', weighting_function = 'Barnes2')
    pyart.io.write_grid(gridded_data_folder + radar_filename, grid)
    os.remove(unzipped_data_folder + radar_filename)
    print(f'Gridding Successful on {radar_filename}')
    return grid