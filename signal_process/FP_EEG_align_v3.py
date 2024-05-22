import misleep
from itertools import groupby
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

############################################################################
data = misleep.load_mat(r'\\172.16.41.188\liyating\Data\FP\20240520_test\5HT_3h\SER_Zscore.mat')
anno = misleep.load_misleep_anno(r'\\172.16.41.188\liyating\Data\FP\20240520_test\5HT_3h\SER.txt')

# Define a time range for consideration, 
# means every state's duration must be greater than the time
consider_time = 5

# Time range in the plot and saved data, half of the total time.
# eg. plot_save_time = 300 means the plot's time range is from -300 to 300
plot_save_time = 300

# Channel in the data you want to analyze
consider_channel = 'Zscore'

# Save params
save_csv_path = r'\\172.16.41.188\liyating\Data\FP\20240520_test\5HT_3h'
save_fig_path = r'\\172.16.41.188\liyating\Data\FP\20240520_test\5HT_3h\SER.pdf'

############################################################################

print('Analysing...')
start_end_anno = anno.start_end
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
                [f'{state[2]}_{next_state[2]}', state[0], round((state[1] + next_state[0])/2, 3), next_state[1]]
            )
_sorted = sorted(transition_points, key=lambda x: x[0])
transition_points_group = [list(each) for _, each in groupby(_sorted, lambda x: x[0])]

# Get data based on each group of transition time points
channel_midata = data.pick_chs(ch_names=[consider_channel])
channel_data = channel_midata.signals[0]
sf = channel_midata.sf[0]

# Draw
signal_figure = plt.figure(figsize=(12, 3*len(transition_points_group)))
signal_ax = signal_figure.subplots(nrows=len(transition_points_group))
signal_figure.set_tight_layout(True)

group_data = {}
for idx, transition_points in enumerate(transition_points_group):
    _name = transition_points[0][0]
    print(f'{_name} is analysing')
    previous_max_length = max([int(each[2]*sf)-int(each[1]*sf) for each in transition_points])
    previous_max_length = max([previous_max_length, int(plot_save_time*sf)])
    later_max_length = max([int(each[3]*sf)-int(each[2]*sf)for each in transition_points])
    later_max_length = max([later_max_length, int(plot_save_time*sf)])
    _name = f'{_name}_{plot_save_time} seconds'
    _temp_lst = []
    for each in transition_points:
        previous_data = channel_data[int(each[1]*sf): int(each[2]*sf)]
        previous_data_padded = np.pad(previous_data, (previous_max_length - len(previous_data), 0), 'constant', constant_values=np.nan)
        later_data = channel_data[int(each[2]*sf): int(each[3]*sf)]
        later_data_padded = np.pad(later_data, (0, later_max_length - len(later_data)), 'constant', constant_values=np.nan)
        _temp_lst.append(np.concatenate(
            [previous_data_padded, later_data_padded]
            )[previous_max_length-int(plot_save_time*sf): 
              previous_max_length+int(plot_save_time*sf)])

    nan_temp_lst = np.array(_temp_lst)
    zero_temp_lst = np.nan_to_num(nan_temp_lst)

    pd.DataFrame(data=np.array(zero_temp_lst).T,
        columns=['->'.join([str(_) for _ in each[1:]]) for each in transition_points]
        ).to_csv(f'{save_csv_path}\{_name}.csv', index=False)

    [signal_ax[idx].plot(each, color='lightgray') for each in nan_temp_lst]
    signal_ax[idx].axvline(int(plot_save_time*sf), color='red', linewidth=2)
    signal_ax[idx].set_xlim(0, int(2*plot_save_time*sf))
    _max = np.max(np.abs(zero_temp_lst))*1.1
    signal_ax[idx].set_ylim(-_max, _max)
    signal_ax[idx].set_title(f'{_name}_{len(transition_points)} trail(s)')
    signal_ax[idx].xaxis.set_ticks(
        [int(each * sf) for each in range(0, 2*plot_save_time+1, int(5*plot_save_time/60))],
        np.arange(-plot_save_time, plot_save_time+1, int(5*plot_save_time/60)),
    )

    # calculate mean line
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        _mean_group_data = np.nanmean(nan_temp_lst, axis=0)
    signal_ax[idx].plot(_mean_group_data, color='black')

signal_figure.savefig(f'{save_fig_path[:-4]}_{plot_save_time}.pdf', dpi=300)

print('Analysation finished!')

plt.show()