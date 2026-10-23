# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""The sound of NVDA itself: its audio sessions on all devices, their channels, the ducking preference,
the voice of the synthesizer, the sounds of NVDA and the speech mode.
"""

from unmuteSupport import (
	SpeechMode,
	audio,
	events,
	later,
	log,
	options,
	runLater,
	speechConfig,
	speechState,
	synth,
)
from unmuteSupport.case import NVDA_PID, AddonTestCase
from unmuteSupport.fakes import float32


class TestNvdaSessions(AddonTestCase):
	def test_sessions_of_nvda_on_all_devices(self):
		headphones = self.world.add("{headphones}")
		first = self.addSession(self.speakers)
		self.addSession(self.speakers, pid=NVDA_PID + 1)
		second = self.addSession(headphones)
		self.assertEqual(self.plugin.getNvdaSessions(), [first, second])

	def test_session_without_a_process_is_skipped(self):
		unknown = self.addSession(self.speakers)
		unknown.noProcess = True
		session = self.addSession(self.speakers)
		self.assertEqual(self.plugin.getNvdaSessions(), [session])
		self.assertIn("Unable to get the process of an audio session", log.warnings)

	def test_muted_and_quiet_sessions_on_every_device_are_turned_on(self):
		headphones = self.world.add("{headphones}")
		muted = self.addSession(self.speakers, level=0.5, mute=1)
		quiet = self.addSession(headphones, level=0.01)
		self.assertTrue(self.plugin.unmuteNvdaSessions())
		self.assertEqual((muted.volume.mute, muted.volume.level), (0, float32(0.5)))
		self.assertEqual(quiet.volume.level, float32(0.2))

	def test_muted_session_alone_is_a_change(self):
		session = self.addSession(self.speakers, mute=1)
		self.assertTrue(self.plugin.unmuteNvdaSessions())
		self.assertEqual((session.volume.mute, session.volume.level), (0, 1.0))

	def test_another_copy_of_nvda_is_not_changed(self):
		other = self.addSession(self.speakers, pid=NVDA_PID + 1, level=0.0, mute=1)
		self.assertFalse(self.plugin.unmuteNvdaSessions())
		self.assertEqual((other.volume.mute, other.volume.level), (1, 0.0))

	def test_closed_session_does_not_stop_the_others(self):
		closed = self.addSession(self.speakers, level=0.0)
		session = self.addSession(self.speakers, level=0.0)
		self.plugin.getNvdaSessions = lambda: [closed, session]
		closed.volume.broken = True
		self.assertTrue(self.plugin.unmuteNvdaSessions())
		self.assertEqual(session.volume.level, float32(0.2))


class TestNvdaChannels(AddonTestCase):
	def test_channels_are_not_changed_without_the_option(self):
		session = self.addSession(self.speakers, channels=[1.0, 0.0])
		self.assertFalse(self.plugin.unmuteNvdaSessions())
		self.assertEqual(session.channels.levels, [1.0, 0.0])

	def test_all_channels_are_restored_if_one_is_quiet(self):
		options["channels"] = True
		session = self.addSession(self.speakers, channels=[0.5, 0.0])
		self.assertTrue(self.plugin.unmuteNvdaSessions())
		self.assertEqual(session.channels.levels, [1.0, 1.0])

	def test_unequal_but_loud_enough_channels_are_not_changed(self):
		options["channels"] = True
		session = self.addSession(self.speakers, channels=[1.0, 0.3])
		self.assertFalse(self.plugin.unmuteNvdaSessions())
		self.assertEqual(session.channels.levels, [1.0, float32(0.3)])

	def test_channels_are_not_changed_while_sound_split_is_enabled(self):
		options["channels"] = True
		audio["soundSplitState"] = 2
		session = self.addSession(self.speakers, channels=[1.0, 0.0])
		self.assertFalse(self.plugin.unmuteNvdaSessions())
		self.assertEqual(session.channels.levels, [1.0, 0.0])


class TestDucking(AddonTestCase):
	def test_sessions_of_nvda_are_not_lowered_during_calls(self):
		options["noducking"] = True
		headphones = self.world.add("{headphones}")
		sessions = [self.addSession(self.speakers), self.addSession(headphones)]
		other = self.addSession(self.speakers, pid=NVDA_PID + 1)
		self.plugin.applyDuckingPreference()
		self.assertEqual([session.optOut for session in sessions], [1, 1])
		self.assertIsNone(other.optOut)

	def test_sessions_of_nvda_are_lowered_again_when_the_option_is_turned_off(self):
		session = self.addSession(self.speakers)
		session.optOut = 1
		self.plugin.applyDuckingPreference()
		self.assertEqual(session.optOut, 0)

	def test_closed_session_does_not_stop_the_others(self):
		options["noducking"] = True
		closed = self.addSession(self.speakers)
		session = self.addSession(self.speakers)
		self.plugin.getNvdaSessions = lambda: [closed, session]
		closed.broken = True
		self.plugin.applyDuckingPreference()
		self.assertEqual(session.optOut, 1)

	def test_applied_again_after_the_synthesizer_has_changed(self):
		options["noducking"] = True
		session = self.addSession(self.speakers)
		self.synthChanged.notify()
		self.assertEqual(events, [("later", 1000, "applyDuckingPreference")])
		later[0][1]()
		self.assertEqual(session.optOut, 1)

	def test_not_applied_after_the_synthesizer_has_changed_without_the_option(self):
		self.synthChanged.notify()
		self.assertEqual(events, [])


class TestSynthVolume(AddonTestCase):
	def test_quiet_voice_is_raised_and_saved(self):
		self.synth.volume = 3
		self.assertTrue(self.plugin.raiseSynthVolume())
		self.assertEqual(self.synth.volume, 20)
		self.assertEqual(speechConfig["espeak"]["volume"], 20)

	def test_voice_at_the_minimum_level_is_not_changed(self):
		self.synth.volume = 5
		self.assertFalse(self.plugin.raiseSynthVolume())
		self.assertEqual(self.synth.volume, 5)

	def test_raised_at_least_to_the_minimum_level(self):
		options.update(volume=10, minlevel=40)
		self.synth.volume = 30
		self.assertTrue(self.plugin.raiseSynthVolume())
		self.assertEqual(self.synth.volume, 40)

	def test_synthesizer_without_volume(self):
		self.synth.volume, self.synth.hasVolume = 0, False
		self.assertFalse(self.plugin.raiseSynthVolume())
		self.assertEqual(self.synth.volume, 0)

	def test_no_synthesizer(self):
		synth["current"] = None
		self.assertFalse(self.plugin.raiseSynthVolume())


class TestSoundsVolume(AddonTestCase):
	def test_quiet_sounds_are_raised(self):
		audio["soundVolume"] = 0
		self.assertTrue(self.plugin.raiseSoundsVolume())
		self.assertEqual(audio["soundVolume"], 20)

	def test_sounds_at_the_minimum_level_are_not_changed(self):
		audio["soundVolume"] = 5
		self.assertFalse(self.plugin.raiseSoundsVolume())
		self.assertEqual(audio["soundVolume"], 5)

	def test_not_changed_while_the_sounds_follow_the_voice(self):
		audio.update(soundVolume=0, soundVolumeFollowsVoice=True)
		self.assertFalse(self.plugin.raiseSoundsVolume())
		self.assertEqual(audio["soundVolume"], 0)

	def test_raised_before_the_sound_of_the_addon_is_played(self):
		audio["soundVolume"] = 0
		self.plugin.unmuteAudio(manual=True)
		self.assertEqual(audio["soundVolume"], 20)
		self.assertEqual(self.sounds(), [("sound", "unmuted.wav")])


class TestSpeechMode(AddonTestCase):
	def test_speech_mode_is_switched_to_talk(self):
		for mode in (SpeechMode.off, SpeechMode.beeps, SpeechMode.onDemand):
			speechState.speechMode = mode
			self.plugin.turnOnSpeechMode()
			self.assertEqual(speechState.speechMode, SpeechMode.talk, mode)

	def test_talk_mode_is_not_set_again(self):
		self.assertFalse(self.plugin.turnOnSpeechMode())
		self.assertEqual(events, [])

	def test_switched_speech_mode_plays_the_sound(self):
		speechState.speechMode = SpeechMode.off
		self.plugin.restoreSoundAndSpeech()
		self.assertEqual(events, [("speechMode", "talk"), ("sound", "unmuted.wav")])

	def test_switched_speech_mode_plays_the_sound_after_the_audio_service_has_started(self):
		speechState.speechMode = SpeechMode.beeps
		self.world.serviceDown = True
		self.plugin.restoreSoundAndSpeech()
		self.world.serviceDown = False
		events.clear()
		while later:
			runLater()
		self.assertEqual(events, [("sound", "unmuted.wav")])

	def test_without_the_option(self):
		options["speechmode"] = False
		speechState.speechMode = SpeechMode.off
		self.plugin.restoreSoundAndSpeech()
		self.assertEqual(speechState.speechMode, SpeechMode.off)
