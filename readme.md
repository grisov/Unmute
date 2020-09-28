# NVDA Unmute

* Author: Oleksandr Gryshchenko
* Version: 1.0
* Download [stable version][1]

This add-on checks the status of the Windows audio system when NVDA starts.
And, if it turns out that the sound is muted - the add-on forcibly turns it on.

## Change log

### Version 1.0. Features of implementation
The add-on uses a third-party module [Windows Sound Manager][2].

## Altering NVDA Unmute
You may clone this repo to make alteration to NVDA Unmute.

### Third Party dependencies
These can be installed with pip:
- markdown
- scons
- python-gettext

### To package the add-on for distribution:
1. Open a command line, change to the root of this repo
2. Run the **scons** command. The created add-on, if there were no errors, is placed in the current directory.

[1]: https://github.com/grisov/Unmute/releases/download/v1.0/unmute-1.0.nvda-addon
[2]: https://github.com/Paradoxis/Windows-Sound-Manager
