# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""The audio devices of Windows: which devices are checked, their mute, volume and channels."""

from unmuteSupport import audio, log, options
from unmuteSupport.case import AddonTestCase
from unmuteSupport.fakes import float32


class TestCheckedDevices(AddonTestCase):
	def test_default_output_device(self):
		self.world.add("{headphones}")
		self.assertEqual(self.plugin.getCheckedDevices(), [self.speakers])

	def test_specific_device_of_nvda_when_switching_is_turned_off(self):
		headphones = self.world.add("{headphones}")
		audio["outputDevice"] = "{headphones}"
		options["switchdevice"] = False
		self.assertEqual(self.plugin.getCheckedDevices(), [self.speakers, headphones])

	def test_specific_device_is_not_checked_when_nvda_is_switched(self):
		self.world.add("{headphones}")
		audio["outputDevice"] = "{headphones}"
		self.assertEqual(self.plugin.getCheckedDevices(), [self.speakers])

	def test_specific_device_that_is_the_default_one_is_checked_once(self):
		audio["outputDevice"] = "{speakers}"
		options["switchdevice"] = False
		self.assertEqual(self.plugin.getCheckedDevices(), [self.speakers])

	def test_unknown_specific_device(self):
		audio["outputDevice"] = "{removed}"
		options["switchdevice"] = False
		self.assertEqual(self.plugin.getCheckedDevices(), [self.speakers])

	def test_no_default_device_but_the_specific_one(self):
		headphones = self.world.add("{headphones}")
		self.world.defaultIndex = None
		audio["outputDevice"] = "{headphones}"
		options["switchdevice"] = False
		self.assertEqual(self.plugin.getCheckedDevices(), [headphones])

	def test_audio_service_not_available(self):
		self.world.serviceDown = True
		self.assertEqual(self.plugin.getCheckedDevices(), [])


class TestUnmuteDevice(AddonTestCase):
	def test_muted_device_is_unmuted_without_changing_its_volume(self):
		self.speakers.volume.mute = 1
		self.assertTrue(self.plugin.unmuteDevice(self.speakers))
		self.assertEqual(self.speakers.volume.mute, 0)
		self.assertEqual(self.speakers.volume.level, float32(0.5))

	def test_too_quiet_device_is_raised_to_the_custom_level(self):
		self.speakers.volume.level = float32(0.04)
		self.assertTrue(self.plugin.unmuteDevice(self.speakers))
		self.assertEqual(self.speakers.volume.level, float32(0.2))

	def test_device_at_the_minimum_level_is_not_changed(self):
		self.speakers.volume.level = float32(0.05)
		self.assertFalse(self.plugin.unmuteDevice(self.speakers))
		self.assertEqual(self.speakers.volume.level, float32(0.05))

	def test_custom_level_lower_than_the_minimum_raises_to_the_minimum(self):
		options.update(volume=10, minlevel=30)
		self.speakers.volume.level = float32(0.25)
		self.assertTrue(self.plugin.unmuteDevice(self.speakers))
		self.assertEqual(self.speakers.volume.level, float32(0.3))
		# The custom volume level in the settings is not changed
		self.assertEqual(options["volume"], 10)

	def test_channels_are_not_changed_without_the_option(self):
		self.speakers.volume.channels = [float32(0.5), 0.0]
		self.assertFalse(self.plugin.unmuteDevice(self.speakers))
		self.assertEqual(self.speakers.volume.channels, [float32(0.5), 0.0])

	def test_each_quiet_channel_is_raised_with_the_option(self):
		options["devicechannels"] = True
		self.speakers.volume.channels = [float32(0.8), 0.0, float32(0.01), float32(0.3)]
		self.assertTrue(self.plugin.unmuteDevice(self.speakers))
		# The other channels are not made equal
		self.assertEqual(
			self.speakers.volume.channels,
			[float32(0.8), float32(0.2), float32(0.2), float32(0.3)],
		)

	def test_loud_enough_channels_are_not_changed(self):
		options["devicechannels"] = True
		self.speakers.volume.channels = [float32(0.8), float32(0.1)]
		self.assertFalse(self.plugin.unmuteDevice(self.speakers))
		self.assertEqual(self.speakers.volume.channels, [float32(0.8), float32(0.1)])

	def test_removed_device_is_logged(self):
		self.speakers.breakDown()
		self.assertFalse(self.plugin.unmuteDevice(self.speakers))
		self.assertTrue(
			any("Unable to turn on the sound of the audio device" in item for item in log.warnings),
		)

	def test_all_devices_are_checked_after_a_removed_one(self):
		headphones = self.world.add("{headphones}", level=0.0)
		audio["outputDevice"] = "{headphones}"
		options.update(switchdevice=False, playsound=False)
		self.speakers.breakDown()
		self.plugin.unmuteAudio()
		self.assertEqual(headphones.volume.level, float32(0.2))
