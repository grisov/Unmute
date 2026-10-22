# A part of the NVDA Unmute add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

import os.path
import addonHandler
from collections.abc import MutableMapping
from comtypes import COMError
from core import callLater
import globalPluginHandler
import synthDriverHandler
from typing import Any, cast, override
from nvwave import playWaveFile
import gui
import tones
import config
from logHandler import log
from .audio import (
	Device,
	getActiveOutputDevices,
	getDefaultOutputDevice,
	getDevice,
	getDeviceId,
	getEndpointVolume,
	getSessionVolume,
	listSessions,
	logDebugWarning,
)

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")

_addon = addonHandler.getCodeAddon()
ADDON_NAME: str = _addon.name
ADDON_SUMMARY: str = _addon.manifest["summary"]

# Attempts to find the default output device when NVDA starts, e.g. while the audio service of Windows is still starting
AUDIO_ATTEMPTS = 10
# Interval between the attempts, in milliseconds
AUDIO_ATTEMPT_INTERVAL = 1000
# Delay before the sound of NVDA is checked again after NVDA has been switched to the default output device,
# in milliseconds: Windows creates the audio session of NVDA on the new device only when NVDA plays a sound there
NVDA_RECHECK_DELAY = 1000


def getNvdaConfig(section: str) -> MutableMapping[str, Any]:
	"""Get a section of the NVDA configuration in the current configuration profile.
	NVDA declares config.conf as None until the configuration is loaded, so its type is given here once.

	:param section: the name of the section, e.g. "audio"
	:return: the section of the configuration
	"""
	return cast(Any, config.conf)[section]


def getAddonConfig() -> MutableMapping[str, Any]:
	"""Get the add-on section of the NVDA configuration in the current configuration profile.

	:return: the options of the add-on
	"""
	return getNvdaConfig(ADDON_NAME)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""

	scriptCategory: str = ADDON_SUMMARY

	@override
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		"""Initialization of the add-on parameters."""
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		confspec = {
			"volume": "integer(default=20,min=0,max=100)",
			"minlevel": "integer(default=5,min=0,max=100)",
			"reinit": "boolean(default=true)",
			"retries": "integer(default=0,min=0,max=10000000)",
			"switchdevice": "boolean(default=true)",
			"playsound": "boolean(default=true)",
		}
		config.conf.spec[ADDON_NAME] = confspec
		from .settings import UnmuteSettingsPanel

		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(UnmuteSettingsPanel)
		callLater(0, self.unmuteAudio)
		if config.conf[ADDON_NAME]["reinit"]:
			callLater(0, self.resetSynth, 0)

	@override
	def terminate(self) -> None:
		"""This will be called when NVDA is finished with this global plugin"""
		from .settings import UnmuteSettingsPanel

		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(UnmuteSettingsPanel)
		except IndexError:
			log.warning("Can't remove %s Settings panel from NVDA settings dialogs", ADDON_SUMMARY)
		super().terminate()

	def getTargetLevel(self) -> float:
		"""Get the volume level set for an audio device or NVDA when its volume is lower than the minimum level.
		The level is at least the minimum level, even if the custom volume level in the settings is lower.

		:return: the volume level (from 0.0 to 1.0)
		"""
		addonConfig = getAddonConfig()
		return max(addonConfig["volume"], addonConfig["minlevel"]) / 100.0

	def getCheckedDevices(self) -> list[Device]:
		"""Get the audio devices whose sound is turned on: the default output device of Windows and,
		if NVDA uses a specific output device and is not switched to the default one, that device too.
		The devices are got at the moment of the check: they may change while NVDA is running.

		:return: the audio devices, empty if the audio service of Windows is not available
		"""
		devices: list[Device] = []
		default = getDefaultOutputDevice()
		if default is not None:
			devices.append(default)
		outputDevice: str = getNvdaConfig("audio")["outputDevice"]
		if outputDevice != "default" and not getAddonConfig()["switchdevice"]:
			device = getDevice(outputDevice)
			if device is not None and getDeviceId(device) not in [getDeviceId(item) for item in devices]:
				devices.append(device)
		return devices

	def unmuteDevice(self, device: Device) -> bool:
		"""Turn on the sound of the audio device if it is muted, and raise its volume if it is too low.
		An error is logged, so the other devices and steps are checked anyway.

		:param device: the audio device
		:return: whether the volume level has been raised
		"""
		try:
			volume = getEndpointVolume(device)
			if volume.GetMute():
				volume.SetMute(0, None)
			if volume.GetMasterVolumeLevelScalar() * 100.0 < getAddonConfig()["minlevel"]:
				volume.SetMasterVolumeLevelScalar(self.getTargetLevel(), None)
				return True
		except COMError:
			logDebugWarning(f"Unable to turn on the sound of the audio device {getDeviceId(device)}")
		return False

	def unmuteAudio(self, attempt: int = 1) -> None:
		"""Turn on Windows sound if it is muted or low.
		NVDA is switched to the default output device first, so the sound is turned on where NVDA plays it.
		If there is no default output device, e.g. the audio service of Windows is still starting
		after logging on, the check is repeated a few times.

		:param attempt: the number of the attempt, from 1
		"""
		if getDefaultOutputDevice() is None and attempt < AUDIO_ATTEMPTS:
			# core.callLater of NVDA has no type annotations
			cast(Any, callLater)(AUDIO_ATTEMPT_INTERVAL, self.unmuteAudio, attempt + 1)
			return
		switched = getAddonConfig()["switchdevice"] and self.switchToDefaultOutputDevice()
		# Every device is checked, not only until the first raised one
		raised = [self.unmuteDevice(device) for device in self.getCheckedDevices()]
		raised.append(self.unmuteNvdaProcess())
		# The sound is played once, when the sound of NVDA itself has been turned on too
		if (any(raised) or switched) and getAddonConfig()["playsound"]:
			self.audioEnabledSound()
		if switched:
			cast(Any, callLater)(NVDA_RECHECK_DELAY, self.recheckNvdaProcess)

	def recheckNvdaProcess(self) -> None:
		"""Check the sound of NVDA again after NVDA has been switched to the default output device
		and has played a sound there, so its audio session on that device exists.
		"""
		if self.unmuteNvdaProcess() and getAddonConfig()["playsound"]:
			self.audioEnabledSound()

	def unmuteNvdaProcess(self) -> bool:
		"""Turn on the sound of NVDA itself if it is muted or low: all audio sessions of the running NVDA process
		on all active output devices, because Windows keeps the volume of a program for each device.
		The process is found by its ID, so other copies of NVDA (e.g. a portable one) are not changed.
		An error is logged, so the other sessions and steps are checked anyway.

		:return: whether the volume level of any audio session of NVDA has been raised
		"""
		raised = False
		processId = os.getpid()
		for device in getActiveOutputDevices():
			for session in listSessions(device):
				try:
					if session.GetProcessId() != processId:
						continue
					volume = getSessionVolume(session)
					if volume.GetMute():
						volume.SetMute(0, None)
					if volume.GetMasterVolume() * 100.0 < getAddonConfig()["minlevel"]:
						volume.SetMasterVolume(self.getTargetLevel(), None)
						raised = True
				except COMError:
					logDebugWarning("Unable to turn on the sound of an audio session of NVDA")
		return raised

	def resetSynth(self, retry_count: int) -> None:
		"""If the synthesizer is not initialized - repeat attempts to initialize it."""
		if not synthDriverHandler.getSynth():
			synthDriverHandler.initialize()
			synthDriverHandler.setSynth(str(config.conf["speech"]["synth"]))
			retries = config.conf[ADDON_NAME]["retries"]
			if retry_count <= retries or retries == 0:
				callLater(1000, self.resetSynth, retry_count + 1)

	def switchToDefaultOutputDevice(self) -> bool:
		"""Switch NVDA audio output to the default output device of Windows.

		:return: whether NVDA has been switched, False if it already uses the default device
		"""
		audioConfig = getNvdaConfig("audio")
		if audioConfig["outputDevice"] == "default":
			return False
		audioConfig["outputDevice"] = "default"
		# The synthesizer is restarted to use the new output device. If it is not initialized yet,
		# it uses the new device when it is initialized
		synth = synthDriverHandler.getSynth()
		if synth is not None and synthDriverHandler.setSynth(synth.name):
			tones.terminate()
			tones.initialize()
		return True

	def audioEnabledSound(self) -> None:
		"""The sound when the audio is successfully turned on and the synthesizer is enabled."""
		try:
			playWaveFile(os.path.join(os.path.dirname(__file__), "unmuted.wav"))
		except Exception:
			pass
