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
			"volume": "integer(default=90,min=0,max=100)",
			"minlevel": "integer(default=20,min=0,max=100)",
			"reinit": "boolean(default=true)",
			"retries": "integer(default=0,min=0,max=10000000)",
			"playsound": "boolean(default=true)"
		}
		config.conf.spec[_addonName] = confspec
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(UnmuteSettingsPanel)
		# Variables initialization for using Core Audio Windows API
		device = AudioUtilities.GetSpeakers()
		interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
		self._volume = cast(interface, POINTER(IAudioEndpointVolume))
		# Value for adjusting the volume of the system sound
		self._stepChange = 0.01
		self._speakersName = self.getSpeakersName(device)
		# Switch between processes
		self._index = 0
		self._selectedProcess = ''
		Thread(target=self.unmuteAudio).start()
		if config.conf[_addonName]['reinit']:
			Thread(target=self.resetSynth).start()

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
			config.conf[_addonName]['volume'] = max(config.conf[_addonName]['volume'], config.conf[_addonName]['minlevel'])
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

	def getSpeakersName(self, device) -> str:
		"""Get the default audio device name based on its ID.
		@param device: default audio device instance
		@type device: pycaw.pycaw.IMMDevice
		@return: human friendly name of transferred device instance
		@rtype: str
		"""
		try:
			devices = AudioUtilities.GetAllDevices()
		except Exception as e:
			devices = []
		for dev in devices:
			if device.GetId()==dev.id:
				return dev.FriendlyName
		# Translators: Used as the default audio device name when the device name could not be determined
		return _("Default audio device")

	def audioEnabledSound(self) -> None:
		"""The sound when the audio is successfully turned on and the synthesizer is enabled."""
		try:
			nvwave.playWaveFile(os.path.join(os.path.dirname(__file__), "unmuted.wav"))
		except:
			pass

	def announceVolumeLevel(self, volumeLevel: float) -> None:
		"""Announce the current volume level.
		@param volumeLevel: value of volume level
		@type volumeLevel: float, from 0.0 to 1.0
		"""
		# Translators: The message is announced during volume control
		ui.message("%s %d" % (_("Volume"), int(volumeLevel*100)))

	def announceIsMuted(self) -> None:
		"""Announce that the sound was muted."""
		# Translators: The message is announced during volume control
		ui.message(_("The sound is muted"))

	# Translators: The name of the method that displayed in the NVDA input gestures dialog
	@script(description=_("Increase the volume"))
	def script_volumeUp(self, gesture):
		"""Increase the volume of the selected sound source.
		@param gesture: the input gesture in question
		@type gesture: L{inputCore.InputGesture}
		"""
		if self._index != 0:
			for session in AudioUtilities.GetAllSessions():
				if session.Process and session.Process.name()==self._selectedProcess:
					interface = session.SimpleAudioVolume
					volumeLevel = interface.GetMasterVolume()
					if volumeLevel<=self._stepChange and interface.GetMute():
						interface.SetMute(False, None)
					volumeLevel = min(1.0, volumeLevel + self._stepChange)
					interface.SetMasterVolume(volumeLevel, None)
		else:
			volumeLevel = self._volume.GetMasterVolumeLevelScalar()
			if volumeLevel<=self._stepChange and self._volume.GetMute():
				self._volume.SetMute(False, None)
			volumeLevel = min(1.0, volumeLevel + self._stepChange)
			self._volume.SetMasterVolumeLevelScalar(volumeLevel, None)
		self.announceVolumeLevel(volumeLevel)

	# Translators: The name of the method that displayed in the NVDA input gestures dialog
	@script(description=_("Decrease the volume"))
	def script_volumeDown(self, gesture):
		"""Decrease the volume of the selected sound source.
		@param gesture: the input gesture in question
		@type gesture: L{inputCore.InputGesture}
		"""
		if self._index != 0:
			for session in AudioUtilities.GetAllSessions():
				if session.Process and session.Process.name()==self._selectedProcess:
					interface = session.SimpleAudioVolume
					volumeLevel = interface.GetMasterVolume()
					volumeLevel = max(0.0, volumeLevel - self._stepChange)
					if volumeLevel > 0.0:
						interface.SetMasterVolume(volumeLevel, None)
						self.announceVolumeLevel(volumeLevel)
					else:
						interface.SetMute(True, None)
						self.announceIsMuted()
		else:
			volumeLevel = self._volume.GetMasterVolumeLevelScalar()
			volumeLevel = max(0.0, volumeLevel - self._stepChange)
			if volumeLevel > 0.0:
				self._volume.SetMasterVolumeLevelScalar(volumeLevel, None)
				self.announceVolumeLevel(volumeLevel)
			else:
				self._volume.SetMute(True, None)
				self.announceIsMuted()

	# Translators: The name of the method that displayed in the NVDA input gestures dialog
	@script(description=_("Switch to the next audio source"))
	def script_nextProcess(self, gesture):
		"""Switch to the next audio source (audio device or process).
		@param gesture: the input gesture in question
		@type gesture: L{inputCore.InputGesture}
		"""
		sessions = [s for s in AudioUtilities.GetAllSessions() if s.Process and s.Process.name]
		self._index = (self._index+1) % (len(sessions)+1)
		self._selectedProcess = sessions[self._index-1].Process.name() if self._index!=0 else ''
		title = ' '.join(self._selectedProcess.split('.')[:-1]) if self._selectedProcess else self._speakersName
		ui.message(title)

	# Translators: The name of the method that displayed in the NVDA input gestures dialog
	@script(description=_("Switch to the previous audio source"))
	def script_prevProcess(self, gesture):
		"""Switch to the previous audio source (audio device or process).
		@param gesture: the input gesture in question
		@type gesture: L{inputCore.InputGesture}
		"""
		sessions = [s for s in AudioUtilities.GetAllSessions() if s.Process and s.Process.name]
		self._index = (self._index-1) % (len(sessions)+1)
		self._selectedProcess = sessions[self._index-1].Process.name() if self._index!=0 else ''
		title = ' '.join(self._selectedProcess.split('.')[:-1]) if self._selectedProcess else self._speakersName
		ui.message(title)

	__gestures = {
		"kb:NVDA+windows+upArrow": "volumeUp",
		"kb:NVDA+windows+downArrow": "volumeDown",
		"kb:NVDA+windows+rightArrow": "nextProcess",
		"kb:NVDA+windows+leftArrow": "prevProcess"
	}