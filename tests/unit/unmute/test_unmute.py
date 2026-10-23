# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""Turning on the sound as a whole: the order of the steps, the sound of the add-on, the attempts while
the audio service of Windows is starting, switching NVDA to the default device and the synthesizer.
"""

from unmuteSupport import SpeechMode, audio, events, later, options, runLater, speechState, synth
from unmuteSupport.case import AddonTestCase
from unmuteSupport.fakes import float32

SOUND = ("sound", "unmuted.wav")


class TestSound(AddonTestCase):
	def test_no_sound_when_nothing_has_been_turned_on(self):
		self.plugin.unmuteAudio()
		self.assertEqual(events, [])

	def test_sound_once_when_several_things_have_been_turned_on(self):
		self.speakers.volume.level = 0.0
		self.addSession(self.speakers, level=0.0)
		self.synth.volume = 0
		self.plugin.unmuteAudio()
		self.assertEqual(events, [SOUND])

	def test_no_sound_without_the_option(self):
		options["playsound"] = False
		self.speakers.volume.level = 0.0
		self.plugin.unmuteAudio()
		self.assertEqual(events, [])
		self.assertEqual(self.speakers.volume.level, float32(0.2))

	def test_command_always_plays_the_sound(self):
		options["playsound"] = False
		self.plugin.script_unmute(None)
		self.assertEqual(events, [SOUND])

	def test_unmuted_device_alone_plays_the_sound(self):
		self.speakers.volume.mute = 1
		self.plugin.unmuteAudio()
		self.assertEqual(self.speakers.volume.mute, 0)
		self.assertEqual(events, [SOUND])

	def test_unmuted_session_of_nvda_alone_plays_the_sound(self):
		self.addSession(self.speakers, mute=1)
		self.plugin.unmuteAudio()
		self.assertEqual(events, [SOUND])

	def test_command_plays_the_sound_once_after_several_changes(self):
		self.speakers.volume.mute = 1
		self.addSession(self.speakers, level=0.0)
		speechState.speechMode = SpeechMode.off
		self.plugin.script_unmute(None)
		self.assertEqual(self.sounds(), [SOUND])

	def test_error_of_the_sound_is_logged(self):
		from unmuteSupport import log, sound

		sound["fails"] = True
		self.plugin.script_unmute(None)
		self.assertTrue(any("unmuted.wav" in error for error in log.errors))

	def test_sound_file_exists(self):
		import os

		from unmuteSupport import ADDON_DIR

		self.assertTrue(os.path.isfile(ADDON_DIR / "unmuted.wav"))


class TestSwitchingDevice(AddonTestCase):
	def test_nvda_is_switched_first_and_checked_again_later(self):
		audio["outputDevice"] = "{headphones}"
		self.plugin.unmuteAudio()
		self.assertEqual(audio["outputDevice"], "default")
		self.assertEqual(
			events,
			[
				("setSynth", "espeak", "default"),
				"tones.terminate",
				"tones.initialize",
				SOUND,
				("later", 1000, "recheckNvdaSessions"),
			],
		)

	def test_second_check_turns_on_the_new_session_of_nvda(self):
		audio["outputDevice"] = "{headphones}"
		self.plugin.unmuteAudio()
		session = self.addSession(self.speakers, level=0.0)
		events.clear()
		runLater()
		self.assertEqual(session.volume.level, float32(0.2))
		self.assertEqual(events, [SOUND])

	def test_switching_alone_plays_the_sound_without_a_second_one(self):
		audio["outputDevice"] = "{headphones}"
		self.plugin.unmuteAudio()
		self.addSession(self.speakers)
		runLater()
		self.assertEqual(self.sounds(), [SOUND])

	def test_second_check_with_nothing_to_turn_on(self):
		audio["outputDevice"] = "{headphones}"
		self.plugin.unmuteAudio()
		events.clear()
		runLater()
		self.assertEqual(events, [])

	def test_nvda_already_uses_the_default_device(self):
		self.assertFalse(self.plugin.switchToDefaultOutputDevice())
		self.assertEqual(events, [])

	def test_switching_turned_off(self):
		options["switchdevice"] = False
		audio["outputDevice"] = "{headphones}"
		self.plugin.unmuteAudio()
		self.assertEqual(audio["outputDevice"], "{headphones}")
		self.assertEqual(events, [])

	def test_synthesizer_not_initialized_yet(self):
		synth["current"] = None
		audio["outputDevice"] = "{headphones}"
		self.assertTrue(self.plugin.switchToDefaultOutputDevice())
		self.assertEqual(audio["outputDevice"], "default")
		self.assertEqual(events, [])

	def test_synthesizer_fails_to_restart(self):
		synth["starts"] = False
		audio["outputDevice"] = "{headphones}"
		self.assertTrue(self.plugin.switchToDefaultOutputDevice())
		self.assertEqual(events, [("setSynth", "espeak", "default")])


class TestAudioServiceStarting(AddonTestCase):
	def test_attempts_are_repeated_while_there_is_no_default_device(self):
		self.world.serviceDown = True
		self.plugin.unmuteAudio()
		for _attempt in range(2, 10):
			self.assertEqual(events, [("later", 1000, "unmuteAudio")])
			events.clear()
			runLater()
		self.assertEqual(later[0][2], (10, False, False))

	def test_last_attempt_checks_nvda_anyway(self):
		headphones = self.world.add("{headphones}")
		self.world.defaultIndex = None
		session = self.addSession(headphones, level=0.0)
		self.plugin.unmuteAudio(attempt=10)
		self.assertEqual(later, [])
		self.assertEqual(session.volume.level, float32(0.2))

	def test_sound_is_turned_on_when_the_service_has_started(self):
		self.world.serviceDown = True
		self.speakers.volume.level = 0.0
		self.plugin.unmuteAudio()
		self.world.serviceDown = False
		events.clear()
		runLater()
		self.assertEqual(self.speakers.volume.level, float32(0.2))
		self.assertEqual(events, [SOUND])

	def test_command_keeps_playing_the_sound_after_the_attempts(self):
		self.world.serviceDown = True
		options["reinit"] = False
		self.plugin.script_unmute(None)
		self.world.serviceDown = False
		events.clear()
		runLater()
		self.assertEqual(events, [SOUND])


class TestSynthesizer(AddonTestCase):
	def setUp(self):
		super().setUp()
		synth.update(current=None, starts=False)

	def attempts(self):
		return [event for event in events if event[0] == "setSynth"]

	def test_initialized_synthesizer_is_not_changed(self):
		synth["current"] = self.synth
		self.plugin.initializeSynth(0)
		self.assertEqual(events, [])

	def test_retries_make_one_attempt_more(self):
		options["retries"] = 3
		self.plugin.initializeSynth(0)
		while later:
			runLater()
		self.assertEqual(len(self.attempts()), 4)
		self.assertFalse(self.plugin._initializingSynth)

	def test_no_limit_of_retries(self):
		self.plugin.initializeSynth(0)
		for _ in range(50):
			runLater()
		self.assertEqual(len(self.attempts()), 51)
		self.assertEqual(len(later), 1)

	def test_attempts_stop_when_the_synthesizer_has_started(self):
		self.plugin.initializeSynth(0)
		runLater()
		synth["starts"] = True
		runLater()
		runLater()
		self.assertEqual(len(self.attempts()), 3)
		self.assertEqual(later, [])

	def test_selected_synthesizer_is_initialized(self):
		from unmuteSupport import speechConfig

		speechConfig["synth"] = "oneCore"
		options["retries"] = 1
		self.plugin.initializeSynth(0)
		self.assertEqual(self.attempts(), [("setSynth", "oneCore", "default")])

	def test_command_does_not_start_the_attempts_twice(self):
		options["retries"] = 5
		self.plugin.script_unmute(None)
		self.plugin.script_unmute(None)
		self.assertEqual(len(self.attempts()), 1)
		self.assertEqual(len([call for call in later if call[1].__name__ == "initializeSynth"]), 1)

	def test_without_the_option(self):
		options["reinit"] = False
		self.plugin.restoreSoundAndSpeech()
		self.assertEqual(self.attempts(), [])

	def test_synthesizer_is_initialized_before_its_volume_is_checked(self):
		synth["starts"] = True
		speechState.speechMode = SpeechMode.off
		self.plugin.restoreSoundAndSpeech()
		self.assertEqual(events[:2], [("speechMode", "talk"), ("setSynth", "espeak", "default")])
		self.assertEqual(synth["current"].volume, 100)
