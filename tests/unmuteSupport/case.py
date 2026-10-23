# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""The base class of the tests: a fresh global plugin in a fake audio world for every test."""

from __future__ import annotations
import os
import types
import unittest
from typing import Any

from . import (
	FakeSynth,
	SpeechMode,
	addon,
	audio,
	conf,
	events,
	later,
	log,
	module,
	options,
	speechConfig,
	speechState,
)
from . import sound, synth, synthChanged
from .fakes import AudioWorld, FakeDevice, FakeSession

# The options of the add-on in the tests: the defaults of the add-on, without the checks when the plugin is created
TEST_OPTIONS: dict[str, Any] = {
	"startup": False,
	"volume": 20,
	"minlevel": 5,
	"switchdevice": True,
	"devicechannels": False,
	"channels": False,
	"synthvolume": True,
	"soundsvolume": True,
	"speechmode": True,
	"noducking": False,
	"reinit": True,
	"retries": 0,
	"playsound": True,
	"gestures": False,
}

# The process ID of NVDA in the tests: the process of the tests
NVDA_PID = os.getpid()


class AddonTestCase(unittest.TestCase):
	"""Every test gets a new global plugin and an audio world it controls:

	- self.world: the active output devices of Windows, see fakes.AudioWorld;
	- self.speakers: the default output device, with no audio sessions;
	- self.synth: the initialized synthesizer of NVDA;
	- support.events: sounds, restarts of the synthesizer and tones, delayed calls.
	"""

	def setUp(self) -> None:
		self._patches: list[tuple[Any, str, Any]] = []
		options.clear()
		options.update(TEST_OPTIONS)
		audio.clear()
		audio.update(
			outputDevice="default",
			soundSplitState=0,
			soundVolume=100,
			soundVolumeFollowsVoice=False,
		)
		speechConfig.clear()
		speechConfig.update(synth="espeak", espeak={"volume": 100})
		speechState.speechMode = SpeechMode.talk
		conf.profiles[:] = [type(conf.profiles[0])()]
		conf.rootSection._cache.clear()
		events.clear()
		later.clear()
		log.clear()
		self.synth = FakeSynth("espeak", 100)
		synth.update(current=self.synth, starts=True)
		sound["fails"] = False
		self.world = AudioWorld()
		self.speakers = self.world.add("{speakers}")
		self.patch(
			module("audio"),
			"AudioUtilities",
			types.SimpleNamespace(GetDeviceEnumerator=self.world.enumerator),
		)
		self.categoryClasses.clear()
		self.plugin = self.createPlugin()

	def tearDown(self) -> None:
		self.plugin.terminate()
		for target, name, original in reversed(self._patches):
			setattr(target, name, original)

	@property
	def categoryClasses(self) -> list[Any]:
		"""The panels of the NVDA settings dialog."""
		return addon.gui.settingsDialogs.NVDASettingsDialog.categoryClasses

	def createPlugin(self) -> Any:
		"""Create the global plugin as NVDA does; the plugin of the test is terminated after the test."""
		plugin = addon.GlobalPlugin()
		events.clear()
		return plugin

	def recreatePlugin(self) -> Any:
		"""Terminate the plugin of the test and create a new one with the current options, as NVDA starts."""
		self.plugin.terminate()
		events.clear()
		later.clear()
		self.plugin = addon.GlobalPlugin()
		return self.plugin

	def patch(self, target: Any, name: str, value: Any) -> None:
		"""Replace an attribute for this test only."""
		self._patches.append((target, name, getattr(target, name)))
		setattr(target, name, value)

	def addSession(self, device: FakeDevice, pid: int = NVDA_PID, **kwargs: Any) -> FakeSession:
		"""Add an audio session of a program to the device, of NVDA by default."""
		session = FakeSession(pid, **kwargs)
		device.sessions.append(session)
		return session

	def sounds(self) -> list[Any]:
		"""The sounds played since the start of the test."""
		return [event for event in events if isinstance(event, tuple) and event[0] == "sound"]

	@property
	def synthChanged(self) -> Any:
		return synthChanged
