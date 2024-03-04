% Auto start synapse recording at a specific time
% Xueqiang Wang

% Use diary to save log
diary 'autostart.txt';
diary on;

SDKPATH = 'D:\TDTSDK'; % or whatever path you extracted the SDK zip into
addpath(genpath(SDKPATH));

% Connect to Synapse
syn = SynapseAPI();

% Get current time
currentTime = datetime();

% ############## SET PARAMETERS #####################
% Set time to start
startTime = datetime(2024, 3, 4, 10, 44, 0);
% Set time to stop
stopTime = datetime(2024, 3, 4, 10, 45, 0);
% ###################################################

% If start time is smaller than current time, set it to the current time
if startTime < currentTime
    startTime = currentTime;
    disp('The start time was reset to current time: ' + string(currentTime));
end

% If the recording last less than 1 minute, Error
if minutes(stopTime - startTime) < 1
    disp('The recording was set to start at ' + string(startTime) + ...
    ', stop at ' + string(stopTime) + ...
    ', last for ' + num2str(recordDuration) + ' seconds');
    error('ARE YOU SERIOUS?! (╯°Д°)╯ ┻━┻');
end

% Get the pause time for recording
recordDuration = seconds(stopTime - startTime);
disp('The recording was set to start at ' + string(startTime) + ...
    ', stop at ' + string(stopTime) + ...
    ', last for ' + num2str(recordDuration) + ' seconds');


pauseSeconds = seconds(startTime - currentTime);
disp('Current time: ' + string(currentTime));
disp(['The recording starts after ', num2str(pauseSeconds), ' seconds']);

% Pause until start recording
pause(pauseSeconds);

% Start recording
disp('Recording started at ' + string(datetime()));
syn.setModeStr('Record');
pause(recordDuration);

syn.setModeStr('Idle');
disp('Recording stoped at ' + string(datetime()));
disp(' ');
disp(' ');
