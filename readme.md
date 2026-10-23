# NVDA Unmute

* Author: Oleksandr Gryshchenko
* Version: 1.8
* NVDA compatibility: 2026.1 and beyond
* Download [stable version][1]

This add-on checks the status of the Windows audio system when NVDA starts. And, if it turns out that the sound is muted - the add-on forcibly turns it on.

At the same time, the volume level is checked separately for the NVDA process.

The add-on also checks the status of the speech synthesizer. If there are problems with its initialization, attempts are made to start the synthesizer, which is specified in the NVDA settings.

There is an additional opportunity to check on which audio device the NVDA sound is output. And, if this device differs from the default device, the output automatically switches to the audio device installed in the system as the main one.

Note: If the add-on startup sound always plays even if the NVDA volume is online. That is, the add-on switches the output to the main audio device each time you start NVDA.

This occurs when the audio output device is in the NVDA settings is differ from the default output device or "Microsoft Sound Mapper".

This can be easily solved in one of the following ways:

1. After restarting NVDA, just save the current configuration using NVDA+Ctrl+C. The default audio device will be saved in the NVDA settings and switching will not occur each time when NVDA starts.
2. If you don't want to change the NVDA configuration - just disable the function of switching audio devices in the Unmute settings panel.

## Add-on settings dialog
To open the add-on settings panel, follow these steps:

* Press NVDA+N to open NVDA menu.
* Then go to "Preferences" -> "Settings..." and in the categories list find and open "Unmute Windows Audio".

That's it, you can now use the Tab key to move between add-on settings.

The following options are available in the add-on settings dialog:

1. The first slider in the add-on settings dialog allows you to specify the volume level of Windows, which will be set when you start NVDA if the sound was previously muted or was too low.

2. The minimum Windows volume level at which the volume up procedure will be applied. This slider allows you to adjust the sensitivity level of the add-on.

    If the volume level drops to less than the value specified here, the volume will be increased the next time you start NVDA.

    Otherwise, if the volume level remains higher than the value specified here, then when you restart NVDA, its level will not change.

    And, of course, if the sound was previously turned off, when restarts add-on will turn it on anyway.

3. The following check box allows to enable re-initialization of the voice synthesizer driver.

    This procedure will only start if it is detected at NVDA startup that the voice synthesizer driver has not been initialized.

4. In this field you can specify the number of attempts to re-initialize the voice synthesizer driver. Attempts are performed cyclically with an interval of 1 second. A value of 0 means that attempts will be performed indefinitely until the procedure is successfully completed.

5. The "Switch to the default output audio device" option allows to check at startup the audio device on which NVDA sound is output. And, if this device differs from the default device, the output automatically switches to the audio device installed in the system as the main one.

6. The next checkbox turns on or off playing the startup sound  when the operation is successful.

## Change log
The history of changes for each version of the add-on is published on the [Releases page][2] of the add-on repository.

## Altering of add-on source code
You may clone this repo to make alteration to NVDA Unmute.

### Third Party dependencies
These can be installed with pip:

- markdown
- scons
- python-gettext

### To package the add-on for distribution
1. Open a command line, change to the root of this repo
2. Run the **scons** command. The created add-on, if there were no errors, is placed in the current directory.

[1]: https://addons.nvda-project.org/files/get.php?file=unmute
[2]: https://github.com/grisov/unmute/releases
