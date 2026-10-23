# NVDA Unmute

* Author: Oleksandr Gryshchenko
* Version: 1.8
* NVDA compatibility: 2026.1 and beyond
* Installation: through the NVDA Add-on Store ([stable version][1])

Make sure you can hear NVDA: when NVDA starts, the add-on turns on the muted or too quiet sound of Windows and NVDA and starts the speech synthesizer if it has not started. The same checks can be run at any time with a command.

## When the add-on works
* When NVDA starts. This can be turned off with the "Unmute when NVDA starts" option in the add-on settings.
* With the "Turn on the sound of Windows and NVDA" command, at any time. The command is listed in the NVDA "Input gestures" dialog, in the "Unmute Windows audio" category. You can assign your own shortcut to it there, or turn on the predefined shortcut NVDA+Windows+Shift+U with the "Use the default keyboard shortcut" option in the add-on settings.

After the command the add-on always plays a short sound, so you know that it has worked even if you could hear nothing before. When NVDA starts, the sound is played only if something has been turned on.

## What the add-on checks
Everything below is done only if it is turned on in the add-on settings. A sound is too quiet if its volume is lower than the "Increase the volume if it is lower than" setting; it is then raised to the "Set custom volume level" setting, but never below the minimum level.

1. Speech mode: if the speech of NVDA is off, replaced by beeps or on demand, it is switched to talk. NVDA always starts in the talk mode, so this matters mostly for the command.
2. Synthesizer: if no synthesizer has started, the add-on tries to start the synthesizer selected in the NVDA settings, once a second, as many times as set.
3. Output device: NVDA is switched to the default output device of Windows, so the sound is turned on where NVDA plays it.
4. Windows audio devices: the default output device of Windows is unmuted and its too quiet volume is raised. If NVDA uses a specific output device and is not switched to the default one, that device is checked too. Each muted or too quiet channel of a device can be raised as well, e.g. after the balance has been turned to one side; the other channels are not changed.
5. NVDA itself: the sound of NVDA is unmuted and its too quiet volume is raised on all active output devices, because Windows keeps the volume of a program for each device. Only the running copy of NVDA is changed, not another one, e.g. a portable copy. The add-on can also restore the muted channels of NVDA, raise the too quiet volume of the synthesizer voice and the too quiet volume of NVDA sounds.

If the audio service of Windows is still starting after logging on, the add-on tries again for a few seconds.

When NVDA uses a specific output device in its settings, it is switched to the default device every time NVDA starts, and the short sound is played every time. To avoid this, save the configuration of NVDA after it has been switched (NVDA+Control+C), or turn off the "Switch to the default audio output device" option.

## Calls
When a communication program starts a call, Windows lowers the volume of the other sounds by 80% by default, NVDA included. The "Do not lower the volume of NVDA during calls" option keeps the volume of NVDA unchanged. It concerns only the NVDA process: the communication settings of Windows stay the same, and the sound of the other programs is still lowered during calls.

## Add-on settings
To open the settings, open the NVDA menu (NVDA+N), go to "Preferences", "Settings..." and select the "Unmute Windows audio" category. The settings are saved in the base configuration profile of NVDA and apply at once, without restarting NVDA.

* Unmute when NVDA starts - do everything turned on below when NVDA starts; otherwise only with the command. On by default.
* Volume:
    * Set custom volume level - the volume set for a too quiet audio device, NVDA, its voice or its sounds.
    * Increase the volume if it is lower than - the minimum level: a lower volume is raised.
* Windows audio devices:
    * Switch to the default audio output device - switch NVDA to the default output device of Windows. On by default.
    * Turn on the muted channels of audio devices - raise each too quiet channel of the audio devices. Off by default.
* Screen reader:
    * Turn on the muted channels of NVDA - if any channel of NVDA is too quiet, set all channels of NVDA to the full level, as NVDA does when sound split is turned off. Not available while NVDA sound split is enabled, because sound split sets the channels itself. Off by default.
    * Turn up the volume of the synthesizer voice - raise the too quiet voice; the new volume is saved, as when it is changed with the synth settings ring. On by default.
    * Turn up the volume of NVDA sounds - raise the too quiet beeps and sounds of NVDA before the sound of the add-on is played, so it is heard. Not available while the volume of NVDA sounds follows the voice in the NVDA audio settings. On by default.
    * Switch the speech mode of NVDA to talk. On by default.
    * Do not lower the volume of NVDA during calls - see "Calls". Off by default.
    * Repeat attempts to initialize the voice synthesizer driver - start the synthesizer if it has not started. On by default.
    * Number of retries (0 - infinitely) - how many times to try again, once a second. Available when the attempts are repeated.
* Play sound when audio has been successfully turned on - play a short sound after something has been turned on when NVDA starts. After the command, the sound is always played. On by default.
* Use the default keyboard shortcut - turn the predefined shortcut NVDA+Windows+Shift+U of the command on or off, at once. Off by default.

## Contributions
We are very grateful to everyone who made the effort to develop, translate and maintain this add-on:

* Dang Manh Cuong - Vietnamese translation;
* Cagri Dogan - Turkish translation;
* Christianlm - Italian translation;
* Cary Rowen - simplified Chinese translation;
* Stefan Banita - Polish translation;
* Ivan Novegil Cancelas and Jose Manuel - Spanish and Galician translations;
* Frank Niggemann - German translation;
* Manolo - the sound of the add-on.

## Change log
The history of changes for each version of the add-on is published on the [Releases page][2] of the add-on repository.

## Altering of add-on source code
You may clone this repo to make alterations to NVDA Unmute.

Requirements:

* [uv](https://docs.astral.sh/uv/) - manages Python and all development tools of the add-on;
* [GNU Gettext tools](https://mlocati.github.io/articles/gettext-iconv-windows.html) (`msgfmt` and `xgettext` in the `PATH`) - compile translations and generate the template of translatable strings.

Run the following commands from the root of the repository:

1. `uv sync` - install the development dependencies;
2. `uv run prek run --all-files` - run all code checks: linting and formatting with ruff, type checking with pyright and other checks;
3. `uv run python -m unittest discover -s tests -v` - run the unit tests;
4. `uv run scons` - build the add-on, the created `.nvda-addon` file is placed in the root of the repository;
5. `uv run scons pot` - generate the `.pot` file with all translatable strings of the add-on (optional).

[1]: https://addonstore.nvaccess.org/?channel=stable&addonId=unmute
[2]: https://github.com/grisov/unmute/releases
