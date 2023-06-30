**Remix Light Adjuster**
*Written with the assistance of Bing*

This script adjusts the intensity and/or color temperature values in a file.

## Usage

To use this script, run the following command:

`python adjust_file.py file_path`

where `file_path` is the path to the .usda file to modify.

There are several additional options that can be used with this script:

* `-s` or `--start-line` - This option allows you to specify the line number to start modifying at. The default value is 1.
* `-l` or `--log` - This option enables logging of the changed lines. If this option is used, a log of the changed lines will be printed to the console and written to a file named `changes.log`.
* `-p` or `--percentage` - This option specifies the percentage to adjust the value by. This option is required.
* `-ai` or `--adjust-intensity` - This option enables adjustment of the intensity value using `-p`.
* `-act` or `--adjust-color-temperature` - This option enables adjustment of the color temperature value using `-p`.

For example, to adjust the intensity value in a file named `data.txt`, starting at line 5, and logging the changes, you would run the following command:

`python adjust_file.py data.txt -s 5 -l -ai -p 0.5`

This would adjust the intensity value in all lines containing `float intensity =`, starting at line 5, by multiplying it by 0.5. A log of the changed lines would be printed to the console and written to a file named `changes.log`.

## Description

This script reads the specified file and modifies lines that contain either `float intensity =` or `float colorTemperature =`, depending on which value is being adjusted. The value is multiplied by the specified percentage and the line is updated with the new value. If logging is enabled, a log of the changed lines is printed to the console and written to a file named `changes.log`.

After all lines have been processed, the script prints a message indicating how many lines were changed.
