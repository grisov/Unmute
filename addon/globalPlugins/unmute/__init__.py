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
from threading import Thread
from time import sleep
from tones import beep
from .sound import Sound
import config


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""
	scriptCategory = str(_addonSummary)

	def __init__(self, *args, **kwargs):
		"""Initializing initial configuration values ​​and other fields"""
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		Thread(target=self.unmuteAudio).start()
		Thread(target=self.resetSynth).start()

	def unmuteAudio(self) -> None:
		"""Turns on Windows sound if it is muted or low."""
		if Sound.is_muted() or Sound.current_volume()<15:
			Sound.volume_up()
			Sound.volume_max()
			self.audioEnabled()

	def resetSynth(self) -> None:
		"""If the synthesizer is not initialized - repeat attempts to initialize it."""
		if not synthDriverHandler.getSynth():
			synthDriverHandler.initialize()
			while not synthDriverHandler.getSynth():
				synthDriverHandler.setSynth(config.conf['speech']['synth'])
				sleep(1)
			else:
				self.audioEnabled()

	def audioEnabled(self) -> None:
		"""The signal when the audio is successfully turned on and the synthesizer is enabled."""
		for p,t,s in [(300,100,0.1),(500,80,0.1),(700,60,0.1)]:
			beep(p, t)
			sleep(s)
