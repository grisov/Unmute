# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""The functions of the add-on with the real audio devices of Windows, only reading them:
devices, levels, channels and audio sessions. Nothing is ever set, so the real sound is not changed.
Skipped without an active output device.
"""

import gc
import unittest

from unmuteSupport import module

audio = module("audio")


def activeOutputDevices() -> int:
	try:
		return len(audio.getActiveOutputDevices())
	except Exception:
		return 0


@unittest.skipUnless(activeOutputDevices() > 0, "needs an active audio output device")
class TestRealDevices(unittest.TestCase):
	def setUp(self):
		self.devices = audio.getActiveOutputDevices()

	def test_default_output_device_is_active(self):
		default = audio.getDefaultOutputDevice()
		self.assertIsNotNone(default)
		self.assertIn(audio.getDeviceId(default), [audio.getDeviceId(device) for device in self.devices])

	def test_device_by_its_id(self):
		for device in self.devices:
			deviceId = audio.getDeviceId(device)
			self.assertTrue(deviceId)
			self.assertEqual(audio.getDeviceId(audio.getDevice(deviceId)), deviceId)

	def test_unknown_device(self):
		self.assertIsNone(audio.getDevice("{0.0.0.00000000}.{00000000-0000-0000-0000-000000000000}"))

	def test_levels_and_channels_within_the_range(self):
		for device in self.devices:
			volume = audio.getEndpointVolume(device)
			self.assertTrue(0.0 <= volume.GetMasterVolumeLevelScalar() <= 1.0)
			self.assertIn(volume.GetMute(), (0, 1))
			count = volume.GetChannelCount()
			self.assertGreater(count, 0)
			for channel in range(count):
				self.assertTrue(0.0 <= volume.GetChannelVolumeLevelScalar(channel) <= 1.0)

	def test_sessions_of_every_device(self):
		for device in self.devices:
			for session in audio.listSessions(device):
				self.assertGreaterEqual(session.GetProcessId(), 0)
				volume = audio.getSessionVolume(session)
				self.assertTrue(0.0 <= volume.GetMasterVolume() <= 1.0)
				channels = audio.getSessionChannels(session)
				for channel in range(channels.GetChannelCount()):
					self.assertTrue(0.0 <= channels.GetChannelVolume(channel) <= 1.0)

	def test_repeated_reading_does_not_crash(self):
		# The COM objects are released correctly: ctypes.cast() of COM pointers once crashed NVDA
		for _ in range(30):
			for device in audio.getActiveOutputDevices():
				audio.getEndpointVolume(device).GetMasterVolumeLevelScalar()
				for session in audio.listSessions(device):
					audio.getSessionVolume(session).GetMasterVolume()
			gc.collect()
