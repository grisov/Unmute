# NVDA Unmute

* Author: Oleksandr Gryshchenko
* Version: 1.1
* Download [stable version][1]
* Download [development version][2]

This add-on checks the status of the Windows audio system when NVDA starts. And, if it turns out that the sound is muted - the add-on forcibly turns it on.
The add-on also checks the status of the speech synthesizer. If there are problems with its initialization, attempts are made to start the synthesizer, which is specified in the NVDA settings.

## Add-on settings dialog
The following options are available in the add-on settings dialog:
1. An option that allows to turn on Windows system audio at maximum volume when starting NVDA.
2. If the previous check box is not checked, you can use the next slider to adjust the volume level of the system sound that will be set when starts NVDA.
3. Slider to adjust the value of the minimum volume level at which the first two items will not be applied.

Note: Options 1 and 2 apply in the following cases:
* if Windows system audio was turned off before running NVDA;
* if the system sound level is lower than the value set by slider 3.

4. The following check box allows to enable re-initialization of the voice synthesizer driver.
This procedure will only start if it is detected at NVDA startup that the voice synthesizer driver has not been initialized.

5. In this field you can specify the number of attempts to re-initialize the voice synthesizer driver. Attempts are performed cyclically with an interval of 1 second. A value of 0 means that attempts will be performed indefinitely until the procedure is successfully completed.

## Change log

### Version 1.1
* added add-on settings dialog;
* updated Ukrainian translation.

### Version 1.0.1
* Performs repeated attempts to enabling the synth driver in case of its failed initialization;
* Vietnamese translation added by Dang Manh Cuong;
* Ukrainian translation added.

### Version 1.0. Features of implementation
The add-on uses a third-party module [Windows Sound Manager][3].

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
[2]: https://github.com/grisov/Unmute/releases/download/v1.0/unmute-1.0.nvda-addon
[3]: https://github.com/Paradoxis/Windows-Sound-Manager
