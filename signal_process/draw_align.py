import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math

excel = pd.read_excel(r'E:\workplace\EEGProcessing\00_DATA\DA_PFC\A3_transition.xlsx', sheet_name=None)
save_fig_path = r'E:\workplace\EEGProcessing\00_DATA\DA_PFC\A3_transition.pdf'

sf = 1017.4

signal_figure = plt.figure(figsize=(12, 3*len(excel.keys())))
signal_ax = signal_figure.subplots(nrows=len(excel.keys()))
signal_figure.set_tight_layout(True)

_length = min([each.shape[0] for each in excel.values()])
print(_length)
for idx, key in enumerate(excel.keys()):
    _array = np.array(excel[key]).T
    print(_array.shape)
    [signal_ax[idx].plot(each, color='lightgray') for each in _array]
    signal_ax[idx].plot(np.mean(_array, axis=0), color='black')
    signal_ax[idx].axvline(_length/2, color='red', linewidth=2)
    signal_ax[idx].set_xlim(0, _length)
    _max = np.max(np.abs(_array))*1.5
    signal_ax[idx].set_ylim(-_max, _max)
    signal_ax[idx].set_title(key)

    signal_ax[idx].xaxis.set_ticks(
        [int(each * sf) for each in range(0, math.ceil(_length/sf)+1, 1)],
        np.arange(-math.ceil(_length/sf/2), math.ceil(_length/sf/2)+1, 1),
    )

signal_figure.savefig(save_fig_path, dpi=300)

print('Plot finished!')
plt.show()
