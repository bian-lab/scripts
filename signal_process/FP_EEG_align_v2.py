import misleep
from itertools import groupby
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set params
data = misleep.load_mat(r'E:\workplace\EEGProcessing\00_DATA\OX_PFC\OX_4pin_6mA.mat')
anno = misleep.load_misleep_anno(r'E:\workplace\EEGProcessing\00_DATA\OX_PFC\OX_4pin_6mA.txt')
start_end_anno = anno.start_end

# Define a time range for consideration, 
# means every state's duration must be greater than the time
consider_time = 5
consider_channel = 'd465'
save_excel_path = r'E:\workplace\EEGProcessing\00_DATA\OX_PFC\OX_4pin_6mA.xlsx'
save_fig_path = r'E:\workplace\EEGProcessing\00_DATA\OX_PFC\OX_4pin_6mA.pdf'

print('Analysing...')
# find transition time point
transition_points = []

for idx, state in enumerate(start_end_anno[:-1]):
    next_state = start_end_anno[idx+1]
    # If the previous state and later state have overlap in a second, 
    # make it as a transition time point, 
    # the time point is average of the first state's end and next state's start
    if abs(state[1] - next_state[0]) <= 1:
        # The two states' time must larger than 5 seconds
        if state[1] - state[0] >= consider_time and next_state[1] - next_state[0] > consider_time:
            transition_points.append(
                [f'{state[2]}->{next_state[2]}', state[0], round((state[1] + next_state[0])/2, 3), next_state[1]]
            )

_sorted = sorted(transition_points, key=lambda x: x[0])
transition_points_group = [list(each) for _, each in groupby(_sorted, lambda x: x[0])]

# Get data based on each group of transition time points
channel_midata = data.pick_chs(ch_names=[consider_channel])
channel_data = channel_midata.signals[0]
sf = channel_midata.sf[0]
writer = pd.ExcelWriter(save_excel_path)

# Draw
signal_figure = plt.figure(figsize=(12, 3*len(transition_points_group)))
signal_ax = signal_figure.subplots(nrows=len(transition_points_group))
signal_figure.set_tight_layout(True)

for idx, transition_points in enumerate(transition_points_group):
    _name = transition_points[0][0]
    previous_max_length = max([int(each[2]*sf)-int(each[1]*sf) for each in transition_points])
    later_max_length = max([int(each[3]*sf)-int(each[2]*sf)for each in transition_points])
    _name = f'{_name}_{previous_max_length}'
    _temp_lst = []
    for each in transition_points:
        previous_data = channel_data[int(each[1]*sf): int(each[2]*sf)]
        previous_data_padded = np.pad(previous_data, (0, previous_max_length - len(previous_data)), 'constant', constant_values=0)
        later_data = channel_data[int(each[2]*sf): int(each[3]*sf)]
        later_data_padded = np.pad(later_data, (0, later_max_length - len(later_data)), 'constant', constant_values=0)
        _temp_lst.append(np.concatenate([previous_data_padded, later_data_padded]))

    _temp_lst = np.array(_temp_lst)

    [signal_ax[idx].plot(each, color='lightgray') for each in _temp_lst]
    signal_ax[idx].axvline(previous_max_length, color='red', linewidth=2)
    signal_ax[idx].set_xlim(0, previous_max_length+later_max_length)
    _max = np.mean(np.abs(_temp_lst))*10
    signal_ax[idx].set_ylim(-_max, _max)
    signal_ax[idx].set_title(_name)

    # calculate mean line
    _mean_group_data = np.mean(_temp_lst, axis=0)
    signal_ax[idx].plot(_mean_group_data, color='black')

    # signal_ax[idx].xaxis.set_ticks(
    #     [int(each * sf) for each in range(0, previous_max_length+later_max_length+1, 5)],
    #     np.arange(-previous_max_length, later_max_length+1, 5),
    # )

    _df = pd.DataFrame(data=np.array(_temp_lst).T,
        columns=['->'.join([str(_) for _ in each[1:]]) for each in transition_points])
    
    _df.to_excel(excel_writer=writer, sheet_name=_name, index=False)

signal_figure.savefig(save_fig_path, dpi=300)
writer.close()

print('Analysation finished!')
plt.show()
