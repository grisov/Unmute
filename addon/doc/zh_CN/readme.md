# NVDA Unmute


* 作者： Oleksandr Gryshchenko
* 版本： 1.5.3
* 下载[稳定版][1]
* 下载[开发版][2]

当 NVDA 启动时，此插件会检查 Windows 系统声音状态，如果已静音，则将其打开。
该插件还可以检查语音合成器驱动程序的状态。
如果语音合成器初始化存在问题，则尝试恢复，该合成器是在 NVDA 设置中所指定的合成器。
还有一个功能是检查 NVDA 的默认声音输出设备
如果此设备不是系统默认的设备，则插件会自动切换回系统默认设备。

注意：每次启动 NVDA 时，插件都会将声音切换到 Windows 默认输出设备。
当 NVDA 的输出设备不是“默认输出设备”或“Microsoft 声音映射器”时会进行该调整。
当然，您可以通过以下两种方式调整或禁用该功能：
1. 重新启动NVDA后，只需使用NVDA + Ctrl + C保存当前配置。默认音频设备将保存在NVDA设置中，并且每次 NVDA 启动时都不会自动切换。
2. 如果您不想通过上面方法更改 NVDA 配置，那么只需在 NVDA 设置面板中的“取消系统静音”类别下禁用“切换到默认声音输出设备”功能即可。

## 插件设置对话框

要打开插件设置面板，请按照下列步骤操作：
* 按NVDA + N打开NVDA菜单。
* 找到“选项” ➡ “设置...”，然后在类别列表中找到“取消系统静音”。
这样，您现在可以使用 Tab 键在插件的设置中移动。

插件设置对话框中提供以下选项：

1. 插件设置对话框中的第一个滑块“恢复到的音量级别”，如果系统音量被静音或低于相应级别，则在 NVDA 启动时恢复到该音量。

2. 当音量小于或等于以下值时也会增大音量，
如果音量小于或等于此处指定的值，则下次启动NVDA时音量将增大。
如果音量大于此处指定的值，插件则不会调整。
当然，如果系统音量被静音，则重新启动 NVDA 时无论如何都会自动恢复。

3. 尝试初始化语音合成器驱动程序。
仅当在 NVDA 启动且检测到语音合成器驱动程序尚未初始化时，才尝试该操作。

4. 尝试次数，在这里，您可以指定尝试重新初始化语音合成器驱动程序的次数。
值为 0 表示无限次尝试，直到完成该过程。

5. “切换到默认声音输出设备”
该选项允许在启动时检查NVDA 声音的输出设备。
如果检查到不是默认的声音输出设备，则插件会自动切换。

6. 成功恢复音量后播放声音。

## 升级日志


### 1.5.3版

* 更新了第三方**psutil**模块；
* 添加了“切换到默认声音输出设备”功能。
* 使插件同时兼容 python3.7和3.8版；
* 在插件源代码中添加了 MyPy 类型注释；


### 1.4版
* 增加了针对 NVDA 进程单独增加启动音量的方法；
* 更改了成功恢复音量后的音效（感谢Manolo）；
* 所有的音量控制功能已转移到“volumeAdjustment”插件中。

### 1.3版
* 增加了控制主音量的功能，还可分别针对每个正在运行的应用程序进行控制；
* 更新了越南语的翻译（感谢 Dang Manh Cuong）；
* 添加了土耳其语的翻译（感谢 Cagri Dogan）；
* 添加了意大利语的翻译（感谢 Christianlm）；
* 更新了乌克兰语的翻译；
* 更新了自述文件。

### 1.2版
* 使用了 **Core Audio Windows API** 以代替 **Windows Sound Manager**；
* 添加了通过插件成功打开音频后播放声音；

### 1.1版
* 添加了插件设置对话框；
* 更新了乌克兰语翻译。

### 1.0.1版
* 在语音合成器初始化失败时，反复尝试恢复语音合成器；
*  Dang Manh Cuong添加了越南语的翻译；
* 增加了乌克兰语的翻译。

### 1.0版
实现插件特性，该插件使用了第三方模块Windows Sound Manager。

*译者注： 以下内容适用于开发者，故不再翻译。*
**简体中文由 Eureka 翻译**

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

[1]: https://github.com/grisov/Unmute/releases/download/v1.5/unmute-1.5.nvda-addon
[2]: https://github.com/grisov/Unmute/releases/download/v1.5/unmute-1.5.nvda-addon
