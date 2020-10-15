#-*- coding:utf-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

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
_addonName = _curAddon.manifest['name']
_addonSummary = _curAddon.manifest['summary']

import globalPluginHandler
import synthDriverHandler
import nvwave
import gui
import ui
from scriptHandler import script
from threading import Thread
from time import sleep
import config
from .settings import UnmuteSettingsPanel
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from .pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""
	scriptCategory = _addonSummary

	def __init__(self, *args, **kwargs):
		"""Initializing initial configuration values ​​and other fields"""
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		confspec = {
			"max": "boolean(default=true)",
			"volume": "integer(default=90,min=0,max=100)",
			"minlevel": "integer(default=20,min=0,max=100)",
			"reinit": "boolean(default=true)",
			"retries": "integer(default=0,min=0,max=10000000)",
			"playsound": "boolean(default=true)"
		}
		config.conf.spec[_addonName] = confspec
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(UnmuteSettingsPanel)
		# Initialization of Windows audio subsystem
		devices = AudioUtilities.GetSpeakers()
		interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
		self._volume = cast(interface, POINTER(IAudioEndpointVolume))
		Thread(target=self.unmuteAudio).start()
		if config.conf[_addonName]['reinit']:
			Thread(target=self.resetSynth).start()
		# Value for adjusting the volume of the system sound
		self._stepChange = 0.01

	def terminate(self, *args, **kwargs):
		"""This will be called when NVDA is finished with this global plugin"""
		super().terminate(*args, **kwargs)
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(UnmuteSettingsPanel)
		except IndexError:
			log.warning("Can't remove %s Settings panel from NVDA settings dialogs", _addonSummary)

	def unmuteAudio(self) -> None:
		"""Turns on Windows sound if it is muted or low."""
		if self._volume.GetMute():
			self._volume.SetMute(False, None)
		if self._volume.GetMasterVolumeLevelScalar()*100 < config.conf[_addonName]['minlevel']:
			if config.conf[_addonName]['max']:
				self._volume.SetMasterVolumeLevelScalar(1.0, None)
			else:
				self._volume.SetMasterVolumeLevelScalar(float(config.conf[_addonName]['volume'])/100, None)
			if config.conf[_addonName]['playsound']:
				self.audioEnabledSound()

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

	def audioEnabledSound(self) -> None:
		"""The sound when the audio is successfully turned on and the synthesizer is enabled."""
		try:
			nvwave.playWaveFile(os.path.join(os.path.dirname(__file__), "start.wav"))
		except:
			pass

	def setVolumeLevel(self, volumeLevel: float) -> None:
		"""Set the device volume to the specified value and announce it.
		@param volumeLevel: value of volume level
		@type volumeLevel: float, must be between 0.0 and 1.0
		"""
		self._volume.SetMasterVolumeLevelScalar(volumeLevel, None)
		# Translators: The message is announced during volume control
		ui.message("%s %d%%" % (_("Volume"), int(volumeLevel*100)))

	# Translators: The name of the method that displayed in the NVDA input gestures dialog
	@script(description=_("Increase the volume"))
	def script_volumeUp(self, gesture):
		"""Increase the volume of the selected sound source.
		@param gesture: the input gesture in question
		@type gesture: L{inputCore.InputGesture}
		"""
		volumeLevel = self._volume.GetMasterVolumeLevelScalar()
		volumeLevel += self._stepChange
		if volumeLevel > 1.0:
			volumeLevel = 1.0
		self.setVolumeLevel(volumeLevel)

	# Translators: The name of the method that displayed in the NVDA input gestures dialog
	@script(description=_("Decrease the volume"))
	def script_volumeDown(self, gesture):
		"""Decrease the volume of the selected sound source.
		@param gesture: the input gesture in question
		@type gesture: L{inputCore.InputGesture}
		"""
		volumeLevel = self._volume.GetMasterVolumeLevelScalar()
		volumeLevel -= self._stepChange
		if volumeLevel < 0.0:
			volumeLevel = 0.0
		self.setVolumeLevel(volumeLevel)

	__gestures = {
		"kb:NVDA+control+shift+upArrow": "volumeUp",
		"kb:NVDA+control+shift+downArrow": "volumeDown"
	}