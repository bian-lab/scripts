# -*- coding: UTF-8 -*-
"""
@Project: MiSleep 
@File: time_correction.py
@IDE: PyCharm 
@Author: Xueqiang Wang
@Date: 2024/1/30 12:16 
@Description: Correct the acquisition time
"""

import sys
import subprocess

try:
    import datetime
    import pandas as pd
except ImportError as e:
    print(e)
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'pandas'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'datetime'])
finally:
    import datetime
    import pandas as pd


def label2df(labels, correct_time):
    """
    Transfer the original label to dataframe and correct the date time

    Parameters
    ----------
    labels : List
        Marker, stat-end or sleep stage labels
    correct_time : datetime object
        Time for correction

    Returns
    -------
    result_df : dataframe had corrected time
    """

    # Separate the data by `, ` to get a dataframe of sleep stage labels
    df = pd.DataFrame(data=labels, columns=['string'])
    df = df['string'].str.split(', ', expand=True)
    df.columns = ['start_time', 'start_time_sec', 'start_code',
                  'end_time', 'end_time_sec', 'end_code',
                  'state_code', 'state']

    df['start_time'] = df['start_time_sec'].apply(
        lambda x: transfer_time(correct_time, int(x)))

    df['end_time'] = df['end_time_sec'].apply(
        lambda x: transfer_time(correct_time, int(x)))

    return df


def transfer_time(date_time, seconds, date_time_format='%d:%H:%M:%S'):
    """
    Add seconds to the date time and transfer to the target format

    Parameters
    ----------
    date_time : datetime object
        The date time we want to start with, here is the reset acquisition time
    seconds : int
        Seconds going to add to the date_time
    date_time_format : str
        Final format of date_time. Defaults is '%d:%M:%H:%S'

    Returns
    -------
    target_time : str
        Final date time in string format

    Examples
    --------
    Add seconds to the datetime

    >>> import datetime
    >>> original_time = datetime.datetime(2024, 1, 30, 10, 50, 0)
    >>> seconds = 40
    >>> format_ = '%d-%M:%H:%S'
    >>> transfer_time(original_time, seconds, format_)
    '30-10:50:40'
    """

    temp_time = date_time + datetime.timedelta(seconds=seconds)
    return temp_time.strftime(format=date_time_format)


def df2str(df, separator=', '):
    """
    Transfer the dataframe to a string object

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to transfer
    separator : str
        Separator used to split the dataframe columns. Defaults is `, `

    Returns
    -------
    result_str : str
    """

    str_lst = []
    for row in df.iterrows():
        str_lst.append(separator.join(list(row[1])))
    return '\n'.join(str_lst)


# Get arg parameters
label_file_path = sys.argv[1]
reset_acquisition_time_str = sys.argv[2] + ' ' + sys.argv[3]

reset_acquisition_time = datetime.datetime.strptime(
    reset_acquisition_time_str, '%Y-%m-%d %H:%M:%S')
print(f'Label file selected: {label_file_path}\n'
      f"New acquisition time: {reset_acquisition_time_str}"
      )

# Read out the label file and split by `\n` to get each line
label_file = open(label_file_path, 'r').read().split('\n')

# Get the `==========Marker==========` part
marker = label_file[label_file.index('==========Marker==========') + 1:
                    label_file.index('==========Start-End==========')]
marker_str = ''
if len(marker) > 0:
    marker_df = label2df(labels=marker, correct_time=reset_acquisition_time)
    marker_str = '\n' + df2str(marker_df)

# Get the `==========Start-End==========` part
start_end = label_file[label_file.index('==========Start-End==========') + 1:
                       label_file.index('==========Sleep stage==========')]
start_end_str = ''
if len(start_end) > 0:
    start_end_df = label2df(labels=start_end, correct_time=reset_acquisition_time)
    start_end_str = '\n' + df2str(start_end_df)

# Only get the `==========Sleep stage==========` part
sleep_stage = label_file[label_file.index('==========Sleep stage==========') + 1:]
sleep_stage_df = label2df(labels=sleep_stage, correct_time=reset_acquisition_time)
sleep_stage_str = df2str(sleep_stage_df)

# Construct the string for writing
save_time = datetime.datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')
write_str = str(f'READ ONLY! DO NOT EDIT!\n'
                f'4-INIT 3-Wake 2-REM 1-NREM\n'
                f'Save time: {save_time}\n'
                f"Acquisition time: {reset_acquisition_time_str}\n"
                f'{label_file[4]}\n'
                + '==========Marker==========' + marker_str
                + '\n==========Start-End==========' + start_end_str
                + f'\n==========Sleep stage==========\n'
                  f'{sleep_stage_str}'
                )
with open(label_file_path, 'w') as f:
    f.write(write_str)

print(f'Done!')
