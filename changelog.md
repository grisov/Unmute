## Version 1.8.0

### Added

- A command turns on the sound of Windows and NVDA at any time, with the same checks as when NVDA starts. It is listed in the NVDA Input gestures dialog, and its default keyboard shortcut can be turned on in the add-on settings. The sound of the add-on is always played after the command, so you know that it has worked.
- An option turns off the checks when NVDA starts, so the sound is turned on only with the command.
- New options turn on the sound of NVDA in more cases:
  - the muted or too quiet channels of NVDA (not available while NVDA sound split is enabled);
  - the muted channels of the audio devices, e.g. after the balance has been turned to one side;
  - a too quiet voice of the synthesizer;
  - too quiet NVDA sounds (not available while the volume of the sounds follows the voice);
  - the speech mode of NVDA, which is switched to talk if speech is off, replaced by beeps or on demand.
- An option keeps the volume of NVDA when Windows lowers the other sounds during calls. It changes only NVDA: the communication settings of Windows and the other programs are not changed.
- If the audio service of Windows is still starting after logging on, the add-on tries again for a few seconds.

### Changed

- The audio sessions of NVDA are found on all active output devices, not only on the default one, because Windows keeps the volume of a program for each device. Only the running copy of NVDA is changed, not another one, e.g. a portable copy.
- NVDA is switched to the default output device first, and the sound is turned on there. If NVDA uses a specific output device and the switching is turned off, that device is checked too.
- A too quiet audio device, NVDA, its voice and its sounds are all raised to the custom volume level, at least the minimum level.
- The settings are grouped: the volume, the Windows audio devices and the screen reader.
- The sound of the add-on is played once, after all checks.
- The keyboard shortcut of the custom volume level in the add-on settings is now V, so all shortcuts of the settings are unique.
- The add-on works with the audio devices directly instead of the pycaw helpers that read all properties of a device, so the checks when NVDA starts are faster.
- Tested with NVDA 2026.3.

### Fixed

- The saved settings did not apply until NVDA was restarted.
- The add-on changed the custom volume level in the settings when it raised a too quiet audio device.
- An error of a disconnected audio device stopped the other checks, e.g. turning on the sound of NVDA.
- When the audio service of Windows was not available yet after logging on, the sound was not turned on.
- An error when NVDA was switched to the default output device before the synthesizer was initialized.
- The add-on made one attempt more to initialize the synthesizer than set in the settings.
- The keyboard shortcut of the number of attempts to initialize the synthesizer did not work.
- An error on NVDA exit when the add-on settings panel had already been removed.
