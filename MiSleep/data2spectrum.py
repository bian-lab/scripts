# -*- coding: UTF-8 -*-
"""
@Project: scripts 
@File: data2spectrum.py
@IDE: PyCharm 
@Author: Xueqiang Wang
@Date: 2024/2/1 15:58 
@Description:  Select data and label files, specify a channel to do spectrum analysis, filter is
                optional, output the relative signal power of 0~30 Hz (by default,
                or specified by filter argument) for each sleep state.
                The result excel file include 3 (or 4 if there are INIT labels) sheets.
"""
import os.path

import numpy as np
import pandas as pd
from hdf5storage import loadmat
import sys

from matplotlib import pyplot as plt
from scipy import signal
from scipy.signal import welch


def signal_filter(data, sf=305., btype='lowpass', low=0.5, high=30):
    """
    Filter the signal data, use butter filter in scipy

    Parameters
    ----------
    data : 1D-array
        Signal data need to be filtered.
    sf : float
        Sampling frequency of signal data. Default is 305.
    btype : {'lowpass', 'highpass', 'bandpass'}, optional
        The type of filter. Default is 'lowpass'.
    low : float
        Higher than this frequency can pass, used in 'highpass' and 'bandpass'
        filter. Default is 0.5.
    high : float
        Lower than this frequency can pass, used in 'lowpass' and 'bandpass'
        filyer. Default is 30.

    Returns
    ----------
    filtered_data : 1D-array
        Filtered data of signal data using butter filter

    """
    if btype == 'lowpass':
        fnorm = high / (.5 * sf)
    elif btype == 'highpass':
        fnorm = low / (.5 * sf)
    elif btype == 'bandpass':
        fnorm = np.divide([low, high], .5 * sf)
    else:
        raise ValueError("'%s' is an invalid type for filter, "
                         "you can only choose 'lowpass', 'highpass' or 'bandpass'"
                         % btype)

    # Use irrfilter of scipy.signal to construct a filter
    b, a = signal.iirfilter(N=3, Wn=fnorm, btype=btype, analog=False,
                            output='ba', ftype='butter', fs=None)

    filtered_data = signal.filtfilt(b=b, a=a, x=data)

    return filtered_data


def get_channel_data(data_path, channel):
    """
    Get specific channel data of original data in the matlab format

    Parameters
    ----------
    data_path : str
        Path of original data
    channel : int
        The channel data going to extract
    Returns
    -------
    target_data : 1-D array
        data of the specified channel
    """
    original_data = list(loadmat(data_path).values())[-1]
    if original_data.shape[0] > original_data.shape[1]:
        original_data = original_data.T

    return original_data[channel]


def get_label(label_path):
    """
    Get label array [(start_sec, end_sec, state), ...] with label path
    Parameters
    ----------
    label_path : str
        Path of label

    Returns
    -------
    result_label : 1-D array
        labels like:
            [(start_sec, end_sec, state),
            ...
            ]
    sf : int
        Sampling frequency in the label file
    """
    try:
        label_file = open(label_path, 'r').read().split('\n')
        sleep_stage = [each.split(', ') for each in
                       label_file[label_file.index('==========Sleep stage==========') + 1:]]
        sf = int(label_file[4].split(': ')[-1])
        return [(int(each[1]), int(each[4]), int(each[6])) for each in sleep_stage], sf

    except Exception as e:
        # Exception when label file is invalid
        sys.exit("Select a valid MiSleep label file!")


def cal_draw_spectrum(data, sf, nperseg, freq_band=None):
    """
    Calculate the relative power spectrum of data, and plot

    Parameters
    ----------
    data : 1-D array
        data for calculation
    sf : int
        sampling frequency of data
    nperseg : int
        for welch fourier transform
    freq_band : list
        frequency band low and high frequency

    Returns
    -------
    spectrum : 2-D array
        spectrum frequency and power
    figure : matplotlib.figure()
        spectrum figure
    """
    if freq_band is None:
        freq_band = [0.5, 30]
    F, P = welch(data, sf, nperseg=nperseg)

    # find frequency band
    idx_band = np.logical_and(F >= freq_band[0], F <= freq_band[1])
    F = F[idx_band]
    P = P[idx_band]

    # Get relative power
    P_sum = sum(P)
    P = [each/P_sum for each in P]

    major_ticks_top = np.linspace(0, 50, 26)
    minor_ticks_top = np.linspace(0, 50, 51)

    figure = plt.figure(figsize=(10, 7))
    ax = figure.subplots(nrows=1, ncols=1)
    plt.subplots_adjust(top=0.95, left=0.15, bottom=0.15, right=0.95)

    ax.xaxis.set_ticks(major_ticks_top)
    ax.xaxis.set_ticks(minor_ticks_top, minor=True)
    ax.grid(which="major", alpha=0.6)
    ax.grid(which="minor", alpha=0.3)

    ax.set_xlim(filter_low, filter_high)
    ax.plot(F, P)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power spectral density (Power/Hz)")

    return np.array([F, P]), figure


################
# 0. Arguments #
################
# Get arguments passed in
data_path = r'E:\workplace\scripts\MiSleep\data\mouse1.mat'
label_path = r'E:\workplace\scripts\MiSleep\data\mouse1_label.txt'
channel = 3

# filter arguments, optional, default is 0.5~30 Hz bandpass
filter_type = 'bandpass'  # 'lowpass' 'highpass' or 'bandpass'
filter_low = 0.5
filter_high = 30

# Output folder
output_folder = r'E:\workplace\scripts\MiSleep\data\test_out'
# if the folder doesn't exist, create it
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

##########################################################
# 1. Get the specific channel data and label information #
##########################################################
channel_data = get_channel_data(data_path=data_path, channel=channel)
label, sf = get_label(label_path=label_path)

################
# 2. Do filter #
################
filter_data = signal_filter(data=channel_data, sf=sf, btype=filter_type,
                            low=filter_low, high=filter_high)

###########################
# 3. Merge 4 states' data #
###########################
NREM_data = [filter_data[each[0]*sf: each[1]*sf] for each in label if each[2] == 1]
NREM_data = [element for sublist in NREM_data for element in sublist]
REM_data = [filter_data[each[0]*sf: each[1]*sf] for each in label if each[2] == 2]
REM_data = [element for sublist in REM_data for element in sublist]
Wake_data = [filter_data[each[0]*sf: each[1]*sf] for each in label if each[2] == 3]
Wake_data = [element for sublist in Wake_data for element in sublist]
Init_data = [filter_data[each[0]*sf: each[1]*sf] for each in label if each[2] == 4]
Init_data = [element for sublist in Init_data for element in sublist]

######################################################
# 4. Get spectrum data for each sleep state and plot #
######################################################
writer = pd.ExcelWriter(output_folder+'/power_results.xlsx')
nperseg = 10*sf

NREM_spec, NREM_figure = cal_draw_spectrum(data=NREM_data, sf=sf, nperseg=nperseg)
REM_spec, REM_figure = cal_draw_spectrum(data=REM_data, sf=sf, nperseg=nperseg)
Wake_spec, Wake_figure = cal_draw_spectrum(data=Wake_data, sf=sf, nperseg=nperseg)
name_map = {
    1: 'NREM',
    2: 'REM',
    3: 'Wake',
    4: 'Init'
}

# Save figure
NREM_figure.savefig(output_folder+'/NREM_spectrum.pdf')
REM_figure.savefig(output_folder+'/REM_spectrum.pdf')
Wake_figure.savefig(output_folder+'/Wake_spectrum.pdf')

# Write to excel file
for idx, spec in enumerate([NREM_spec, REM_spec, Wake_spec]):
    _df = pd.DataFrame(data=spec.T, columns=['frequency', 'power'])
    _df.to_excel(excel_writer=writer, sheet_name=name_map[idx+1], index=False)
if len(Init_data) > sf*10:
    Init_spec, Init_figure = cal_draw_spectrum(data=Init_data, sf=sf, nperseg=nperseg)
    _df = pd.DataFrame(data=Init_spec.T, columns=['frequency', 'power'])
    _df.to_excel(excel_writer=writer, sheet_name=name_map[4], index=False)
    Init_figure.savefig(output_folder + '/Init_spectrum.pdf')

writer.close()










