# MaidReadingsProcessor (Marp)

Console application made with Python 3 for processing records written by [MaidModule](https://github.com/Ggorets0dev/maid-arduino-module) to its portable ROM device.

<p align='center'>
    <img height=225 src="pics/Maid_Logo_icon.png"/>
</p>

## Installation

> **Note:** Requires [Python 3](https://www.python.org)

At the moment, installation is only possible by **cloning the repository** and **installing dependencies** from requirements.txt.

## Input file

### **Structure**

Input file is the result of [MaidModule](https://github.com/Ggorets0dev/maid-arduino-module) writing data to the SD card about the speed and voltage of the battery while driving. Consists of:

* Headers ( {H} tag, date and time of initialization, wheel parameters )
* Readings ( {R} tag, number of pulses per period, raw volt reading from the board )

You can see their templates using the **template** command, values and data types are listed there.

### **Sequence**

First the Header is written during initialization, then the Readings are written after it in turn. The cycle starts again when the device is switched off and on.

### **Limits**

Maximum line limit for the input file is **10.5 million** units. This corresponds to about half a year of use with 8 hours of riding and storing values every 500 milliseconds.

### **Checks**

On input, each file is checked to make sure that the time sequence is maintained and that the lines match the template. Many operations will be rejected if the checks fail, so it is not recommended to change the files manually.

## Processing

### **Commands**

List of available commands for use:

| Title | Description | Verified file required |
|:------|:------------|:----------------------:|
| show | Displaying values with variable names | yes |
| alias | Setting aliases for faster launching of commands | no |
| calc | Calculation of various indicators based on speed and volts | yes |
| check | Checking files in manual mode for temporal consistency and matching strings to templates | no |
| graph | Drawing bar graphs using calculated values | yes |
| reduce | Removing unnecessary lines and duplicate headers from the file | no |
| split | Splitting a file into several parts for more convenient analysis | no |
| template | Displaying templates of different available data structures | no |

### **Display parameters**

In some commands, displaying or calculation options can be (must be) selected:

| Title | Count | Description | Incorrect input causes an error | Default |
|:----------|:-----:|:------------|:-------------------------------:|:-------:|
| date-time | 1 - 2 | Date and time where the values should be (one value for the beam and two for the interval) (ends inclusive) | yes | - |
| date | 1 - 2 | Date where the values should be (one value for the beam and two for the interval) (ends inclusive) | yes | - |
| accuracy | 1 | Number of decimal places for calculated values | no | 2 |

### **Config**

Following values can be edited in the config:

| Title | Description | Default |
|:------|:------------|:-------:|
| minimal_voltage_search | Voltage value below which the variants are not taken into account in the calculations (but are taken into account in the display) | 12 |
| normal_speed_interval | If the output speed falls out of this interval, it is marked as abnormal | 0 - 80 |
| normal_voltage_interval | If the output voltage falls out of this interval, it is marked as abnormal | 0 - 60 |

### **Errors**

The following expections may be obtained by the user while interacting with the software:

| Title | Code | Description |
|:------|:----:|:------------|
| ResourceSizeExceededError | 1 | File specified as a resource has a number of lines greater than the maximum |
| ResourceNotFoundError | 2 | File specified as the source was not detected on the device |
| ResourceWrongEncodingError | 3 | Source file is not UTF-8 encoded (the only supported encoding) |
| ReadingWithoutHeaderError | 4 | An entry (reading) was detected that does not have an attachment to the header |
| CalledAsModuleError | 5 | Main script is called as a module in another script, not by the user from the command line |
| InvalidDateTimePassedError | 6 | Invalid format value is passed as an argument to filter date and time |
| InvalidDatePassedError | 7 | Invalid format value is passed as an argument to filter date |
| InvalidResourceError | 8 | Resource did not pass validation by time sequence or pattern matching |

When an error occurs, its name and code are necessarily displayed in the console, so that the user can get information about it from the manual.
