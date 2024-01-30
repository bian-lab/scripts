## MiSleep scripts

Some scripts about MiSleep

#### Time correction

When you forgot to change the acquisition time when first time create the label file, and you had already labeled some data, you can use the `time_correction.py` to change the acquisition time of your label file

- **Usage**

Firstly please ensure that you have python on your computer.
Download the `time_correction.py` file to your own computer. You need to prepare two arguments, one is the label file path, another is the acquistion time you want to reset, use the `YYYY-MM-DD hh:mm:ss` format for the acquisition time.
Run the following in your command (`cmd` when you use Windows).

```shell
python PATH_TO_TIME_CORRECTION.PY/time_correction.py PATH_TO_YOUR_LABEL_FILE/LABEL.txt NEW_ACQUISITION_TIME

# Here is an example, when you put the time_correction.py and
# the label file in the same directory, and now you are in the directory.
python time_correction.py label.txt 2024-01-30 13:20:20
```

And if you want to know how it works, check the `time_correction.ipynb`, which you can open with `jupyter notebook`, I covered each step in detail in that file.
