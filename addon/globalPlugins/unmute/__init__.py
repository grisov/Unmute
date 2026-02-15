# A part of the NVDA Unmute add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020-2026 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

import os.path
import addonHandler
from core import callLater
from ctypes import POINTER
import globalPluginHandler
import synthDriverHandler
from typing import Any, cast, override
from nvwave import playWaveFile
import gui
import tones
import config
from logHandler import log
from pycaw.utils import AudioUtilities, AudioDevice, ISimpleAudioVolume, IAudioEndpointVolume
from utils.mmdevice import getOutputDevices

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")

_addon = addonHandler.getCodeAddon()
ADDON_NAME: str = _addon.name
ADDON_SUMMARY: str = _addon.manifest["summary"]


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""

	scriptCategory: str = ADDON_SUMMARY
	_device: AudioDevice | None = None
	_volume: POINTER(IAudioEndpointVolume) | None = None

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
		# Variables initialization for using Core Audio Windows API
		try:
			self._device = cast(AudioDevice, AudioUtilities.GetSpeakers())
			if self._device:
				self._volume = cast(POINTER(IAudioEndpointVolume), self._device.EndpointVolume)
		except Exception:
			log.exception("Unmute: Failed to initialize audio devices")
			self._volume = None
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

	def unmuteAudio(self) -> None:
		"""Turn on Windows sound if it is muted or low."""
		if not self._volume:
			return
		if self._volume.GetMute():
			self._volume.SetMute(False, None)
		if self._volume.GetMasterVolumeLevelScalar() * 100 < config.conf[ADDON_NAME]["minlevel"]:
			config.conf[ADDON_NAME]["volume"] = max(
				config.conf[ADDON_NAME]["volume"],
				config.conf[ADDON_NAME]["minlevel"],
			)
			self._volume.SetMasterVolumeLevelScalar(float(config.conf[ADDON_NAME]["volume"]) / 100.0, None)
			if config.conf[ADDON_NAME]["playsound"]:
				self.audioEnabledSound()
		self.unmuteNvdaProcess()
		if config.conf[ADDON_NAME]["switchdevice"]:
			self.switchToDefaultOutputDevice()

	def unmuteNvdaProcess(self) -> None:
		"""Turn on NVDA process sound if it is muted or low."""
		for session in AudioUtilities.GetAllSessions():
			if session.Process and session.Process.name().lower() == "nvda.exe":
				volume = cast(POINTER(ISimpleAudioVolume), session.SimpleAudioVolume)
				if volume.GetMute():
					volume.SetMute(False, None)
				if volume.GetMasterVolume() * 100.0 < config.conf[ADDON_NAME]["minlevel"]:
					volume.SetMasterVolume(float(config.conf[ADDON_NAME]["volume"]) / 100.0, None)
					if config.conf[ADDON_NAME]["playsound"]:
						self.audioEnabledSound()

	def resetSynth(self, retry_count: int) -> None:
		"""If the synthesizer is not initialized - repeat attempts to initialize it."""
		if not synthDriverHandler.getSynth():
			synthDriverHandler.initialize()
			synthDriverHandler.setSynth(str(config.conf["speech"]["synth"]))
			retries = config.conf[ADDON_NAME]["retries"]
			if retry_count <= retries or retries == 0:
				callLater(1000, self.resetSynth, retry_count + 1)

	def getDefaultDeviceID(self) -> str:
		"""Obtain the default output audio device ID.
		@return: default output audio device ID
		@rtype: str
		"""
		try:
			devices = cast(list[AudioDevice], AudioUtilities.GetAllDevices())
		except Exception:
			devices = []
		defaultDevice = next(filter(lambda dev: dev.id == self._device.id, devices), None)
		defaultDeviceID = defaultDevice.id if defaultDevice else "default"
		outputDeviceIDs = [device[0] for device in getOutputDevices(includeDefault=True)]
		if outputDeviceIDs[0] == "":
			outputDeviceIDs[0] = "default"
		return next(
			filter(lambda id: id in defaultDeviceID or defaultDeviceID in id, outputDeviceIDs),
			outputDeviceIDs[0],
		)

	def switchToDefaultOutputDevice(self) -> None:
		"""Switch NVDA audio output to the default audio device."""
		device: str = "default"  # self.getDefaultDeviceID()
		if config.conf["audio"]["outputDevice"] not in ("default", device):
			config.conf["audio"]["outputDevice"] = device
			if synthDriverHandler.setSynth(synthDriverHandler.getSynth().name):
				tones.terminate()
				tones.initialize()
				if config.conf[ADDON_NAME]["playsound"]:
					self.audioEnabledSound()

	def audioEnabledSound(self) -> None:
		"""The sound when the audio is successfully turned on and the synthesizer is enabled."""
		try:
			playWaveFile(os.path.join(os.path.dirname(__file__), "unmuted.wav"))
		except Exception:
			pass
