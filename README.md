# MaidReadingsProcessor (Marp)

Console application made with Python 3 for processing records written by [MaidModule](https://github.com/Ggorets0dev/maid-arduino-module) to its portable ROM device.

<p align='center'>
    <img height=225 src="pics/Maid_Logo_icon.png"/>
</p>

## Installation

---
Two starting options are provided:

* Download the source code using an archive or git clone, then install dependencies, **run through Python 3.**

* Download the installer from the Releases page. Run it and then use the executable file. **Does not require Python 3.** *(Coming later)*

> **Note:** Running the immediate source code gives you the ability to open releases that have not been created as executable. Checks are performed each time before the release executable is loaded, but dynamically loaded libraries may not work correctly.

## Tech

---

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
| InvalidResourceError | 7 | Resource did not pass validation by time sequence or pattern matching |

When an error occurs, its name and code are necessarily displayed in the console, so that the user can get information about it from the manual.
