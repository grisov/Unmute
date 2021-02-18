#-*- coding:utf-8 -*-
# A part of the NVDA Unmute add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020-2021 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

from __future__ import annotations
from typing import List
import addonHandler
from logHandler import log
try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to initialise translations. This may be because the addon is running from NVDA scratchpad.")

import os
_addonDir = os.path.join(os.path.dirname(__file__), "..", "..")
if isinstance(_addonDir, bytes):
	_addonDir = _addonDir.decode("mbcs")
_curAddon = addonHandler.Addon(_addonDir)
_addonName, _addonSummary = _curAddon.manifest['name'], _curAddon.manifest['summary']

import globalPluginHandler
import synthDriverHandler
import nvwave
import gui
import ui
import tones
from threading import Thread
from time import sleep
import config
from .settings import UnmuteSettingsPanel
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from .pycaw import AudioUtilities, IAudioEndpointVolume


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""
	scriptCategory: str = _addonSummary

	def __init__(self, *args, **kwargs) -> None:
		"""Initializing initial configuration values ​​and other fields"""
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		confspec = {
			"volume": "integer(default=20,min=0,max=100)",
			"minlevel": "integer(default=5,min=0,max=100)",
			"reinit": "boolean(default=true)",
			"retries": "integer(default=0,min=0,max=10000000)",
			"switchdevice": "boolean(default=true)",
			"playsound": "boolean(default=true)"
		}
		config.conf.spec[_addonName] = confspec
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(UnmuteSettingsPanel)
		# Variables initialization for using Core Audio Windows API
		self._device = AudioUtilities.GetSpeakers()
		interface = self._device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
		self._volume = cast(interface, POINTER(IAudioEndpointVolume))
		Thread(target=self.unmuteAudio).start()
		if config.conf[_addonName]['reinit']:
			Thread(target=self.resetSynth).start()

	def terminate(self, *args, **kwargs) -> None:
		"""This will be called when NVDA is finished with this global plugin"""
		super().terminate(*args, **kwargs)
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(UnmuteSettingsPanel)
		except IndexError:
			log.warning("Can't remove %s Settings panel from NVDA settings dialogs", _addonSummary)

	def unmuteAudio(self) -> None:
		"""Turn on Windows sound if it is muted or low."""
		if self._volume.GetMute():
			self._volume.SetMute(False, None)
		if self._volume.GetMasterVolumeLevelScalar()*100 < config.conf[_addonName]['minlevel']:
			config.conf[_addonName]['volume'] = max(config.conf[_addonName]['volume'], config.conf[_addonName]['minlevel'])
			self._volume.SetMasterVolumeLevelScalar(float(config.conf[_addonName]['volume'])/100, None)
			if config.conf[_addonName]['playsound']:
				self.audioEnabledSound()
		self.unmuteNvdaProcess()
		if config.conf[_addonName]['switchdevice']:
			self.switchToDefaultOutputDevice()

	def unmuteNvdaProcess(self) -> None:
		"""Turn on NVDA process sound if it is muted or low."""
		for session in AudioUtilities.GetAllSessions():
			if session.Process and session.Process.name().lower()=="nvda.exe":
				volume = session.SimpleAudioVolume
				if volume.GetMute():
					volume.SetMute(False, None)
				if volume.GetMasterVolume()*100 < config.conf[_addonName]['minlevel']:
					volume.SetMasterVolume(float(config.conf[_addonName]['volume'])/100, None)
					if config.conf[_addonName]['playsound']:
						self.audioEnabledSound()
				return

	def resetSynth(self) -> None:
		"""If the synthesizer is not initialized - repeat attempts to initialize it."""
		if not synthDriverHandler.getSynth():
			synthDriverHandler.initialize()
			i = 0
			while not synthDriverHandler.getSynth() and i<=config.conf[_addonName]['retries']:
				synthDriverHandler.setSynth(config.conf['speech']['synth'])
				sleep(1)
				if config.conf[_addonName]['retries']!=0:
					i+=1
			else:
				if config.conf[_addonName]['playsound']:
					self.audioEnabledSound()

	def getDefaultDeviceName(self) -> str:
		"""Obtain the default output audio device name.
		@return: default output audio device name
		@rtype: str
		"""
		try:
			devices: List[str] = AudioUtilities.GetAllDevices()
		except Exception:
			devices: List[str] = []
		defaultDevice = next(filter(lambda dev: dev.id==self._device.GetId(), devices), None)
		defaultDeviceName = defaultDevice.FriendlyName if defaultDevice else '[undefined device]'
		devices = nvwave.getOutputDeviceNames()
		if devices[0] in ("", "Microsoft Sound Mapper"):
			devices[0] = "Microsoft Sound Mapper"
		return next(filter(lambda name: name in defaultDeviceName or defaultDeviceName in name, devices), devices[0])

	def switchToDefaultOutputDevice(self) -> None:
		"""Switch NVDA audio output to the default audio device."""
		device: str = self.getDefaultDeviceName()
		if config.conf['speech']['outputDevice'] not in ["Microsoft Sound Mapper", device]:
			config.conf['speech']['outputDevice'] = device
			if synthDriverHandler.setSynth(synthDriverHandler.getSynth().name):
				tones.terminate()
				tones.initialize()
				if config.conf[_addonName]['playsound']:
					self.audioEnabledSound()

	def audioEnabledSound(self) -> None:
		"""The sound when the audio is successfully turned on and the synthesizer is enabled."""
		try:
			nvwave.playWaveFile(os.path.join(os.path.dirname(__file__), "unmuted.wav"))
		except Exception:
			pass
