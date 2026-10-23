# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""Access to Windows Core Audio: the devices, their volume and the audio sessions, with errors of Windows."""

from unmuteSupport import log, module
from unmuteSupport.case import AddonTestCase
from unmuteSupport.fakes import comError

audio = module("audio")


class TestDevices(AddonTestCase):
	def test_default_output_device(self):
		self.world.add("{headphones}")
		self.assertIs(audio.getDefaultOutputDevice(), self.speakers)

	def test_no_default_output_device(self):
		self.world.defaultIndex = None
		self.assertIsNone(audio.getDefaultOutputDevice())

	def test_audio_service_not_available(self):
		self.world.serviceDown = True
		self.assertIsNone(audio.getDefaultOutputDevice())
		self.assertIsNone(audio.getDevice("{speakers}"))
		self.assertEqual(audio.getActiveOutputDevices(), [])

	def test_device_by_its_id(self):
		headphones = self.world.add("{headphones}")
		self.assertIs(audio.getDevice("{headphones}"), headphones)

	def test_unknown_device(self):
		self.assertIsNone(audio.getDevice("{unknown}"))

	def test_active_output_devices_in_the_order_of_windows(self):
		headphones = self.world.add("{headphones}")
		self.assertEqual(audio.getActiveOutputDevices(), [self.speakers, headphones])

	def test_device_removed_while_listed_is_skipped(self):
		headphones = self.world.add("{headphones}")
		self.world.removedWhileListed = {0}
		self.assertEqual(audio.getActiveOutputDevices(), [headphones])

	def test_id_of_a_removed_device_is_empty(self):
		self.speakers.breakDown()
		self.assertEqual(audio.getDeviceId(self.speakers), "")

	def test_volume_of_the_device(self):
		self.assertIs(audio.getEndpointVolume(self.speakers), self.speakers.volume)

	def test_volume_of_a_removed_device_raises_com_error(self):
		self.speakers.breakDown()
		with self.assertRaises(type(comError())):
			audio.getEndpointVolume(self.speakers)


class TestSessions(AddonTestCase):
	def test_sessions_of_any_device(self):
		headphones = self.world.add("{headphones}")
		session = self.addSession(headphones, pid=42)
		self.assertEqual(audio.listSessions(headphones), [session])
		self.assertEqual(audio.listSessions(self.speakers), [])

	def test_empty_and_closed_sessions_are_skipped(self):
		first = self.addSession(self.speakers, pid=1)
		self.speakers.sessions.append(None)
		closed = self.addSession(self.speakers, pid=2)
		closed.broken = True
		last = self.addSession(self.speakers, pid=3)
		self.assertEqual(audio.listSessions(self.speakers), [first, last])

	def test_sessions_of_a_removed_device_are_empty(self):
		self.addSession(self.speakers)
		self.speakers.breakDown()
		self.assertEqual(audio.listSessions(self.speakers), [])

	def test_volume_and_channels_of_a_session(self):
		session = self.addSession(self.speakers)
		self.assertIs(audio.getSessionVolume(session), session.volume)
		self.assertIs(audio.getSessionChannels(session), session.channels)

	def test_debug_warning_is_logged_with_the_error(self):
		self.world.serviceDown = True
		audio.getDefaultOutputDevice()
		self.assertIn("Unable to get the default output audio device", log.warnings)
