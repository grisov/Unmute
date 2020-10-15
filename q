[1mdiff --git a/readme.md b/readme.md[m
[1mindex 8267878..f5458d6 100644[m
[1m--- a/readme.md[m
[1m+++ b/readme.md[m
[36m@@ -1,21 +1,47 @@[m
 # NVDA Unmute[m
 [m
 * Author: Oleksandr Gryshchenko[m
[31m-* Version: 1.0[m
[32m+[m[32m* Version: 1.2[m
 * Download [stable version][1][m
[32m+[m[32m* Download [development version][2][m
 [m
 This add-on checks the status of the Windows audio system when NVDA starts. And, if it turns out that the sound is muted - the add-on forcibly turns it on.[m
 The add-on also checks the status of the speech synthesizer. If there are problems with its initialization, attempts are made to start the synthesizer, which is specified in the NVDA settings.[m
 [m
[32m+[m[32m## Add-on settings dialog[m
[32m+[m[32mThe following options are available in the add-on settings dialog:[m
[32m+[m[32m1. An option that allows to turn on Windows system audio at maximum volume when starting NVDA.[m
[32m+[m[32m2. If the previous check box is not checked, you can use the next slider to adjust the volume level of the system sound that will be set when starts NVDA.[m
[32m+[m[32m3. Slider to adjust the value of the minimum volume level at which the first two items will not be applied.[m
[32m+[m
[32m+[m[32mNote: Options 1 and 2 apply in the following cases:[m
[32m+[m[32m* if Windows system audio was turned off before running NVDA;[m
[32m+[m[32m* if the system sound level is lower than the value set by slider 3.[m
[32m+[m
[32m+[m[32m4. The following check box allows to enable re-initialization of the voice synthesizer driver.[m
[32m+[m[32mThis procedure will only start if it is detected at NVDA startup that the voice synthesizer driver has not been initialized.[m
[32m+[m
[32m+[m[32m5. In this field you can specify the number of attempts to re-initialize the voice synthesizer driver. Attempts are performed cyclically with an interval of 1 second. A value of 0 means that attempts will be performed indefinitely until the procedure is successfully completed.[m
[32m+[m
[32m+[m[32m6. The next checkbox turns on or off playing the startup sound  when the operation is successful.[m
[32m+[m
 ## Change log[m
 [m
[32m+[m[32m### Version 1.2[m
[32m+[m[32m* switched to using the **pycaw** module instead of **Windows Sound Manager**;[m
[32m+[m[32m* added startup sound playback when audio is successfully turned on by add-on.[m
[32m+[m
[32m+[m[32m### Version 1.1[m
[32m+[m[32m* added add-on settings dialog;[m
[32m+[m[32m* updated Ukrainian translation.[m
[32m+[m
 ### Version 1.0.1[m
 * Performs repeated attempts to enabling the synth driver in case of its failed initialization;[m
 * Vietnamese translation added by Dang Manh Cuong;[m
 * Ukrainian translation added.[m
 [m
 ### Version 1.0. Features of implementation[m
[31m-The add-on uses a third-party module [Windows Sound Manager][2].[m
[32m+[m[32mThe add-on uses a third-party module Windows Sound Manager.[m
 [m
 ## Altering NVDA Unmute[m
 You may clone this repo to make alteration to NVDA Unmute.[m
[36m@@ -30,5 +56,5 @@[m [mThese can be installed with pip:[m
 1. Open a command line, change to the root of this repo[m
 2. Run the **scons** command. The created add-on, if there were no errors, is placed in the current directory.[m
 [m
[31m-[1]: https://github.com/grisov/Unmute/releases/download/v1.0/unmute-1.0.nvda-addon[m
[31m-[2]: https://github.com/Paradoxis/Windows-Sound-Manager[m
[32m+[m[32m[1]: https://github.com/grisov/Unmute/releases/download/v1.2/unmute-1.2.nvda-addon[m
[32m+[m[32m[2]: https://github.com/grisov/Unmute/releases/download/v1.2/unmute-1.2.nvda-addon[m
