# -*- coding: UTF-8 -*-
"""
@Project: MiSleep 
@File: transfer_result.py
@IDE: PyCharm 
@Author: Xueqiang Wang
@Date: 2024/1/31 14:41 
@Description:  Transfer the final label results to an excel file
"""

import sys
import subprocess
import pathlib

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


def insert_row(df, idx, row):
    """
    Insert a row to a dataframe in a specific position

    Parameters
    ----------
    df : pandas.DataFrame
        dataframe for operation
    idx : int
        index to insert the row, insert below the row
    row : series
        Row to insert

    Returns
    -------
    result_df : pandas.DataFrame
    """
    if isinstance(row, pd.Series):
        row = pd.DataFrame(row).T
    df = pd.concat([df[:idx], row, df[idx:]], axis=0).reset_index(drop=True)
    return df


def temp_loop4below_row(row, acquisition_time, columns):
    """
    Just for below row repetition
    Returns
    -------

    """

    seconds_ = (int(row['start_time_sec'] / 3600) + 1) * 3600
    previous_row = pd.Series([
        row['start_time'], row['start_time_sec'], '1',
        transfer_time(acquisition_time, seconds_, '%Y-%m-%d %H:%M:%S'),
        seconds_, '0', row['state_code'], row['state']
    ], index=columns)

    new_row = pd.Series([
        transfer_time(acquisition_time, seconds_, '%Y-%m-%d %H:%M:%S'),
        seconds_, ' ',
        transfer_time(acquisition_time, seconds_, '%Y-%m-%d %H:%M:%S'),
        seconds_, ' ', '5', 'MARKER'
    ], index=columns)

    below_row = pd.Series([
        transfer_time(acquisition_time, seconds_ + 1, '%Y-%m-%d %H:%M:%S'),
        seconds_ + 1, '1', row['end_time'], row['end_time_sec'],
        '0', row['state_code'], row['state']
    ], index=columns)

    return previous_row, new_row, below_row


# Get arg parameters
label_file_path = sys.argv[1]
label_file_name = pathlib.Path(label_file_path).name

try:
    result_name = sys.argv[2]  # self define result file name, should be a .xlsx format
    if not label_file_name.endswith('.txt'):
        sys.exit('Select a valid MiSleep label file!')
    if not result_name.endswith('.xlsx'):
        result_name = ''.join(label_file_name.split('.txt')[:-1]) + '.xlsx'
except IndexError as e:
    result_name = ''.join(label_file_name.split('.txt')[:-1]) + '.xlsx'

try:
    label_file = open(label_file_path, 'r').read().split('\n')

    acquisition_time = datetime.datetime.strptime(
        ' '.join(label_file[3].split(' ')[2:]), '%Y-%m-%d %H:%M:%S')
    sampling_rate = int(label_file[4].split(' ')[2])

    ####################################
    # 1. Get the sleep stage dataframe #
    ####################################

    columns = ['start_time', 'start_time_sec', 'start_code',
               'end_time', 'end_time_sec', 'end_code',
               'state_code', 'state']
    sleep_stage = label_file[label_file.index('==========Sleep stage==========') + 1:]
    df = pd.DataFrame(data=sleep_stage, columns=['string'])
    df = df['string'].str.split(', ', expand=True)
except Exception as e:
    sys.exit("Select a valid MiSleep label file!")

df.columns = columns

# Transfer the start and end time to datetime format
df['start_time'] = df['start_time_sec'].apply(
    lambda x: transfer_time(acquisition_time, int(x), '%Y-%m-%d %H:%M:%S'))

df['end_time'] = df['end_time_sec'].apply(
    lambda x: transfer_time(acquisition_time, int(x), '%Y-%m-%d %H:%M:%S'))

# Change the data type
df['start_time_sec'] = df['start_time_sec'].astype(int)
df['end_time_sec'] = df['end_time_sec'].astype(int)

lst = df['start_time_sec'].copy()
lst[0] = 1
df['start_time_sec'] = lst

#################################
# 2. Add MARKER every full hour #
#################################

# Only 2 possible situations, one is end_time_sec % 3600 == 0
# The other one is int(end_time_sec/3600) > int(start_time_sec/3600)
new_df = pd.DataFrame(columns=columns)
for idx, row in df.iterrows():
    if row['end_time_sec'] % 3600 == 0:
        new_df = insert_row(new_df, idx, row)
        # Just add a row and nothing else
        new_row = pd.Series([
            row['end_time'], row['end_time_sec'], ' ',
            row['end_time'], row['end_time_sec'], '5',
            ' ', 'MARKER'
        ], index=columns)
        new_df = insert_row(new_df, new_df.shape[0], row)
        continue

    if int(row['end_time_sec'] / 3600) > int(row['start_time_sec'] / 3600):

        previous_row, new_row, below_row = temp_loop4below_row(row, acquisition_time, columns)

        new_df = insert_row(new_df, new_df.shape[0], previous_row)
        new_df = insert_row(new_df, new_df.shape[0], new_row)
        while int(below_row['end_time_sec'] / 3600) > int(below_row['start_time_sec'] / 3600):
            row = below_row
            previous_row, new_row, below_row = temp_loop4below_row(row, acquisition_time, columns)
            new_df = insert_row(new_df, new_df.shape[0], previous_row)
            new_df = insert_row(new_df, new_df.shape[0], new_row)

        new_df = insert_row(new_df, new_df.shape[0], below_row)
        continue

    new_df = insert_row(new_df, new_df.shape[0], row)

df = new_df
del new_df

df['bout_duration'] = df.apply(
    lambda x: x[4] - x[1] + 1 if x[7] != 'MARKER' else '', axis=1)

#############################
# 3. Analysis for each hour #
#############################

df['hour'] = df['start_time_sec'].apply(lambda x: int(x / 3600) if x % 3600 != 0 else '')
analyse_df = pd.DataFrame()

analyse_df['date_time'] = [df['start_time'][0]] + list(df[df['state'] == 'MARKER']['start_time'])

features = []
for each in df[df['state'] != 'MARKER'].groupby('hour'):
    df_ = each[1]
    temp_lst = []
    for phase in ["NREM", "REM", "Wake", "INIT"]:
        _duration = df_[df_["state"] == phase]["bout_duration"].sum()
        _bout = df_[df_["state"] == phase]["bout_duration"].count()
        temp_lst += [_duration, _bout, round(_duration / _bout, 2)
        if _bout != 0 else 0, round(_duration / 3600, 2)]
    features.append(temp_lst)

analyse_df[['NREM_duration', 'NREM_bout', "NREM_ave", "NREM_percentage",
            'REM_duration', 'REM_bout', "REM_ave", "REM_percentage",
            'WAKE_duration', 'WAKE_bout', "WAKE_ave", "WAKE_percentage",
            'INIT_duration', 'INIT_bout', "INIT_ave", "INIT_percentage"]] = features

analyse_df[
    ['NREM_duration', 'NREM_bout', 'REM_duration', 'REM_bout', 'WAKE_duration',
     'WAKE_bout', 'INIT_duration', 'INIT_bout']
] = analyse_df[
    ['NREM_duration', 'NREM_bout', 'REM_duration', 'REM_bout', 'WAKE_duration',
     'WAKE_bout', 'INIT_duration', 'INIT_bout']].astype(int)

save_path = pathlib.Path(label_file_path).parent.resolve()
writer = pd.ExcelWriter(f'{save_path}/{result_name}', datetime_format='yyyy-mm-dd hh:mm:ss')
pd.concat([df, analyse_df], axis=1).to_excel(
    excel_writer=writer, sheet_name='All', index=False)

writer.close()
print(f'Done!\nLabel file: {save_path}/{label_file_name}\nTransfer result: {save_path}/{result_name}.xlsx')
