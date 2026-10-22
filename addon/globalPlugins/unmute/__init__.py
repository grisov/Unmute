# A part of the NVDA Unmute add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

import os.path
from collections.abc import Callable
from typing import Any, cast, override

import addonHandler
import config
import core
import globalPluginHandler
import gui
import synthDriverHandler
import tones
from comtypes import COMError
from inputCore import InputGesture
from logHandler import log
from nvwave import playWaveFile
from scriptHandler import script

from .audio import (
	Device,
	Session,
	getActiveOutputDevices,
	getDefaultOutputDevice,
	getDevice,
	getDeviceId,
	getEndpointVolume,
	getSessionChannels,
	getSessionVolume,
	listSessions,
	logDebugWarning,
)
from .configuration import (
	ADDON_NAME,
	ADDON_SUMMARY,
	confspec,
	getAddonConfig,
	getNvdaConfig,
	isSoundSplitEnabled,
	optionsSaved,
)
from .settings import UnmuteSettingsPanel

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")
_: Callable[[str], str]

# Attempts to find the default output device when NVDA starts, e.g. while the audio service of Windows is still starting
AUDIO_ATTEMPTS = 10
# Interval between the attempts, in milliseconds
AUDIO_ATTEMPT_INTERVAL = 1000
# Delay before the sound of NVDA is checked again after NVDA has been switched to the default output device,
# in milliseconds: Windows creates the audio session of NVDA on the new device only when NVDA plays a sound there
NVDA_RECHECK_DELAY = 1000
# Interval between the attempts to initialize the synthesizer, in milliseconds
SYNTH_ATTEMPT_INTERVAL = 1000
# The default gesture of the command that turns on the sound, bound if it is enabled in the add-on settings
DEFAULT_GESTURE = "kb:NVDA+windows+shift+u"


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""

	scriptCategory: str = ADDON_SUMMARY

	@override
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		"""Initialization of the add-on parameters."""
		super().__init__(*args, **kwargs)
		# Whether the attempts to initialize the synthesizer are running, so they are not started twice
		self._resettingSynth: bool = False
		# The configuration of NVDA has no type annotations
		cast(Any, config).conf.spec[ADDON_NAME] = confspec
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(UnmuteSettingsPanel)
		self.bindDefaultGesture()
		optionsSaved.register(self.bindDefaultGesture)
		if getAddonConfig()["startup"]:
			# core.callLater of NVDA has no type annotations
			cast(Any, core).callLater(0, self.restoreSoundAndSpeech)

	@override
	def terminate(self) -> None:
		"""This will be called when NVDA is finished with this global plugin"""
		_ = optionsSaved.unregister(self.bindDefaultGesture)
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(UnmuteSettingsPanel)
		except ValueError:
			log.warning("Can't remove %s Settings panel from NVDA settings dialogs", ADDON_SUMMARY)
		super().terminate()

	def bindDefaultGesture(self) -> None:
		"""Bind or unbind the default gesture of the command as set in the add-on settings,
		when the plugin is created and every time the settings are saved, so NVDA does not need to be restarted.
		"""
		# ScriptableObject.bindGestures of NVDA has no type annotations, None unbinds the gesture
		cast(Any, self).bindGestures({DEFAULT_GESTURE: "unmute" if getAddonConfig()["gestures"] else None})

	# Translators: The name of the command in the NVDA input gestures dialog
	@script(description=_("Turn on the sound of Windows and NVDA"))
	def script_unmute(self, gesture: InputGesture) -> None:
		"""Do everything that is done when NVDA starts: turn on the sound of Windows and NVDA
		and initialize the synthesizer if it is not initialized, as enabled in the add-on settings.
		The sound is played even if nothing has been changed: the user may hear nothing before the command,
		so the sound tells that the command has worked and NVDA can be heard.
		"""
		self.restoreSoundAndSpeech(manual=True)

	def restoreSoundAndSpeech(self, manual: bool = False) -> None:
		"""Turn on the sound of Windows and NVDA and, if the synthesizer is not initialized,
		start the attempts to initialize it, as enabled in the add-on settings.

		:param manual: whether the command of the add-on has been used, then the sound is always played
		"""
		self.unmuteAudio(manual=manual)
		if getAddonConfig()["reinit"] and not self._resettingSynth:
			self.resetSynth(0)

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

	def unmuteAudio(self, attempt: int = 1, manual: bool = False) -> None:
		"""Turn on Windows sound if it is muted or low.
		NVDA is switched to the default output device first, so the sound is turned on where NVDA plays it.
		If there is no default output device, e.g. the audio service of Windows is still starting
		after logging on, the check is repeated a few times.

		:param attempt: the number of the attempt, from 1
		:param manual: whether the command of the add-on has been used, then the sound is always played
		"""
		if getDefaultOutputDevice() is None and attempt < AUDIO_ATTEMPTS:
			# core.callLater of NVDA has no type annotations
			cast(Any, core).callLater(AUDIO_ATTEMPT_INTERVAL, self.unmuteAudio, attempt + 1, manual)
			return
		switched = getAddonConfig()["switchdevice"] and self.switchToDefaultOutputDevice()
		# Every device is checked, not only until the first raised one
		raised = [self.unmuteDevice(device) for device in self.getCheckedDevices()]
		raised.append(self.unmuteNvdaProcess())
		# The sound is played once, when the sound of NVDA itself has been turned on too
		if manual or ((any(raised) or switched) and getAddonConfig()["playsound"]):
			self.audioEnabledSound()
		if switched:
			cast(Any, core).callLater(NVDA_RECHECK_DELAY, self.recheckNvdaProcess)

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
		If enabled in the settings, the channels of the sessions are restored too, unless NVDA sound split is enabled.
		An error is logged, so the other sessions and steps are checked anyway.

		:return: whether the volume level or the channels of any audio session of NVDA have been raised
		"""
		raised = False
		processId = os.getpid()
		# Sound split of NVDA sets the levels of the channels itself
		restoreChannels: bool = getAddonConfig()["channels"] and not isSoundSplitEnabled()
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
					if restoreChannels and self.restoreChannels(session):
						raised = True
				except COMError:
					logDebugWarning("Unable to turn on the sound of an audio session of NVDA")
		return raised

	def restoreChannels(self, session: Session) -> bool:
		"""Set the full level to all channels of the audio session if any of them is lower than the minimum level,
		e.g. after one channel of NVDA has been turned down. NVDA restores its channels the same way
		when sound split is turned off. Channels that are just unequal but loud enough are not changed.

		:param session: the audio session of NVDA
		:return: whether the channels have been restored
		:raises COMError: the session is not available anymore
		"""
		channels = getSessionChannels(session)
		count = channels.GetChannelCount()
		minLevel = getAddonConfig()["minlevel"] / 100.0
		if all(channels.GetChannelVolume(channel) >= minLevel for channel in range(count)):
			return False
		for channel in range(count):
			channels.SetChannelVolume(channel, 1.0, None)
		return True

	def resetSynth(self, retryCount: int) -> None:
		"""If the synthesizer is not initialized - repeat attempts to initialize it.

		:param retryCount: the number of the previous attempts
		"""
		self._resettingSynth = False
		if not synthDriverHandler.getSynth():
			synthDriverHandler.initialize()
			_ = synthDriverHandler.setSynth(str(getNvdaConfig("speech")["synth"]))
			retries: int = getAddonConfig()["retries"]
			if retryCount <= retries or retries == 0:
				self._resettingSynth = True
				cast(Any, core).callLater(SYNTH_ATTEMPT_INTERVAL, self.resetSynth, retryCount + 1)

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
		"""The sound when the audio is successfully turned on and the synthesizer is enabled, an error is logged."""
		path = os.path.join(os.path.dirname(__file__), "unmuted.wav")
		try:
			playWaveFile(path)
		except Exception:
			log.error(f"Unable to play {path}", exc_info=True)
