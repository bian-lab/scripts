## Matlab scripts

### Autostart

Auto start the synapse recording at a specific time. Download the [autostart script](./autostart.m) and set the `SDKPATH`, see [TDT add SDKPATH](https://www.tdt.com/docs/sdk/offline-data-analysis/offline-data-matlab/getting-started/#installation). 

Set the **start time** and **stop time**, and run the script. Here we require the recording duration must larger than 1 minute, which is `stop time - start time > 1 min`.

You can **Stop** the script at anytime by clicking the `stop` buttun of MATLAB, while the `Task schedule` we used before didn't seem to be able to stop.

What you need to edit:
```matlab
SDKPATH = 'D:\TDTSDK'; % or whatever path you extracted the SDK zip into

% ############## SET PARAMETERS #####################
% Set time to start
startTime = datetime(2024, 3, 4, 10, 44, 0);
% Set time to stop
stopTime = datetime(2024, 3, 4, 10, 45, 0);
% ###################################################
```