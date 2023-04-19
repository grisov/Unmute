# A part of the NVDA Unmute add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020-2023 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

import addonHandler
import globalPluginHandler
import synthDriverHandler
import nvwave
import gui
import tones
import config
from threading import Thread
from time import sleep
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, pointer
from typing import List
from logHandler import log
from .pycaw import AudioDevice, IMMDevice, AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")

ADDON_NAME: str = addonHandler.getCodeAddon().name
ADDON_SUMMARY: str = addonHandler.getCodeAddon().manifest['summary']

from .settings import UnmuteSettingsPanel  # noqa E402


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""
	scriptCategory: str = ADDON_SUMMARY

	def __init__(self, *args, **kwargs) -> None:
		"""Initialization of the add-on parameters."""
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		confspec = {
			"volume": "integer(default=20,min=0,max=100)",
			"minlevel": "integer(default=5,min=0,max=100)",
			"reinit": "boolean(default=true)",
			"retries": "integer(default=0,min=0,max=10000000)",
			"switchdevice": "boolean(default=true)",
			"playsound": "boolean(default=true)"
		}
		config.conf.spec[ADDON_NAME] = confspec
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(UnmuteSettingsPanel)
		# Variables initialization for using Core Audio Windows API
		self._device: IMMDevice = AudioUtilities.GetSpeakers()
		interface = self._device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
		self._volume: pointer[IAudioEndpointVolume] = cast(interface, POINTER(IAudioEndpointVolume))
		Thread(target=self.unmuteAudio).start()
		if config.conf[ADDON_NAME]['reinit']:
			Thread(target=self.resetSynth).start()

	def terminate(self, *args, **kwargs) -> None:
		"""This will be called when NVDA is finished with this global plugin"""
		super().terminate(*args, **kwargs)
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(UnmuteSettingsPanel)
		except IndexError:
			log.warning("Can't remove %s Settings panel from NVDA settings dialogs", ADDON_SUMMARY)

	def unmuteAudio(self) -> None:
		"""Turn on Windows sound if it is muted or low."""
		if self._volume.GetMute():
			self._volume.SetMute(False, None)
		if self._volume.GetMasterVolumeLevelScalar() * 100 < config.conf[ADDON_NAME]['minlevel']:
			config.conf[ADDON_NAME]['volume'] = max(
				config.conf[ADDON_NAME]['volume'],
				config.conf[ADDON_NAME]['minlevel']
			)
			self._volume.SetMasterVolumeLevelScalar(float(config.conf[ADDON_NAME]['volume']) / 100.0, None)
			if config.conf[ADDON_NAME]['playsound']:
				self.audioEnabledSound()
		self.unmuteNvdaProcess()
		if config.conf[ADDON_NAME]['switchdevice']:
			self.switchToDefaultOutputDevice()

	def unmuteNvdaProcess(self) -> None:
		"""Turn on NVDA process sound if it is muted or low."""
		for session in AudioUtilities.GetAllSessions():
			if session.Process and session.Process.name().lower() == "nvda.exe":
				volume: ISimpleAudioVolume = session.SimpleAudioVolume
				if volume.GetMute():
					volume.SetMute(False, None)
				if volume.GetMasterVolume() * 100.0 < config.conf[ADDON_NAME]['minlevel']:
					volume.SetMasterVolume(float(config.conf[ADDON_NAME]['volume']) / 100.0, None)
					if config.conf[ADDON_NAME]['playsound']:
						self.audioEnabledSound()
				return

	def resetSynth(self) -> None:
		"""If the synthesizer is not initialized - repeat attempts to initialize it."""
		if not synthDriverHandler.getSynth():
			synthDriverHandler.initialize()
			i = 0
			while not synthDriverHandler.getSynth() and i <= config.conf[ADDON_NAME]['retries']:
				synthDriverHandler.setSynth(config.conf['speech']['synth'])
				sleep(1)
				if config.conf[ADDON_NAME]['retries'] != 0:
					i += 1
			else:
				if config.conf[ADDON_NAME]['playsound']:
					self.audioEnabledSound()

	def getDefaultDeviceName(self) -> str:
		"""Obtain the default output audio device name.
		@return: default output audio device name
		@rtype: str
		"""
		try:
			devices: List[AudioDevice] = AudioUtilities.GetAllDevices()
		except Exception:
			devices = []
		defaultDevice = next(filter(lambda dev: dev.id == self._device.GetId(), devices), None)
		defaultDeviceName = defaultDevice.FriendlyName if defaultDevice else '[undefined device]'
		outputDevices = nvwave.getOutputDeviceNames()
		if outputDevices[0] in ("", "Microsoft Sound Mapper"):
			outputDevices[0] = "Microsoft Sound Mapper"
		return next(
			filter(lambda name: name in defaultDeviceName or defaultDeviceName in name, outputDevices),
			outputDevices[0])

	def switchToDefaultOutputDevice(self) -> None:
		"""Switch NVDA audio output to the default audio device."""
		device: str = self.getDefaultDeviceName()
		if config.conf['speech']['outputDevice'] not in ("Microsoft Sound Mapper", device,):
			config.conf['speech']['outputDevice'] = device
			if synthDriverHandler.setSynth(synthDriverHandler.getSynth().name):
				tones.terminate()
				tones.initialize()
				if config.conf[ADDON_NAME]['playsound']:
					self.audioEnabledSound()

	def audioEnabledSound(self) -> None:
		"""The sound when the audio is successfully turned on and the synthesizer is enabled."""
		import os.path
		try:
			nvwave.playWaveFile(os.path.join(os.path.dirname(__file__), "unmuted.wav"))
		except Exception:
			pass
