# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""The settings panel and the options of the add-on in the NVDA configuration."""

import re

from unmuteSupport import audio, conf, controls, module, options
from unmuteSupport.case import AddonTestCase

configuration = module("configuration")
# The groups of the panel, they have no keyboard shortcuts
GROUPS = ["Volume", "Windows audio devices", "Screen reader"]
# The keyboard shortcuts of the NVDA settings dialog itself: &Categories and &Apply
NVDA_SHORTCUTS = {"c", "a"}


def shortcut(label):
	"""The keyboard shortcut of the label, the letter after "&"."""
	match = re.search(r"&(\w)", label)
	return match.group(1).lower() if match else None


class PanelTestCase(AddonTestCase):
	def createPanel(self):
		controls.labels.clear()
		panel = module("settings").UnmuteSettingsPanel()
		panel.makeSettings(None)
		return panel


class TestPanel(PanelTestCase):
	def test_options_are_shown(self):
		options.update(startup=True, volume=33, minlevel=7, devicechannels=True, retries=4, gestures=True)
		panel = self.createPanel()
		self.assertTrue(panel._startupChk.GetValue())
		self.assertEqual(panel._customVolumeSlider.GetValue(), 33)
		self.assertEqual(panel._minVolumeSlider.GetValue(), 7)
		self.assertTrue(panel._deviceChannelsChk.GetValue())
		self.assertEqual(panel._retriesCountSpin.GetValue(), 4)
		self.assertTrue(panel._gesturesChk.GetValue())

	def test_saved_in_the_base_profile_and_applied_at_once(self):
		conf.rootSection._cache["unmute"] = "cached"
		panel = self.createPanel()
		panel._startupChk.SetValue(True)
		panel._gesturesChk.SetValue(True)
		panel._customVolumeSlider.SetValue(40)
		panel.onSave()
		saved = conf.profiles[0]["unmute"]
		self.assertEqual((saved["startup"], saved["gestures"], saved["volume"]), (True, True, 40))
		self.assertNotIn("unmute", conf.rootSection._cache)

	def test_every_option_is_saved(self):
		panel = self.createPanel()
		panel.onSave()
		self.assertEqual(set(conf.profiles[0]["unmute"]), set(configuration.confspec))

	def test_saved_options_update_the_existing_section(self):
		conf.profiles[0]["unmute"] = {"volume": 10, "unknown": 1}
		self.createPanel().onSave()
		self.assertEqual(conf.profiles[0]["unmute"]["unknown"], 1)
		self.assertEqual(conf.profiles[0]["unmute"]["volume"], 20)

	def test_plugin_is_notified_when_the_settings_are_saved(self):
		panel = self.createPanel()
		panel._gesturesChk.SetValue(True)
		# The fake configuration reads the options, not the profile
		options["gestures"] = True
		panel.onSave()
		self.assertEqual(self.plugin.boundGestures, {"kb:NVDA+windows+shift+u": "unmute"})

	def test_channels_of_nvda_not_available_while_sound_split_is_enabled(self):
		self.assertTrue(self.createPanel()._channelsChk.IsEnabled())
		audio["soundSplitState"] = 1
		self.assertFalse(self.createPanel()._channelsChk.IsEnabled())

	def test_sounds_volume_not_available_while_the_sounds_follow_the_voice(self):
		self.assertTrue(self.createPanel()._soundsVolumeChk.IsEnabled())
		audio["soundVolumeFollowsVoice"] = True
		self.assertFalse(self.createPanel()._soundsVolumeChk.IsEnabled())

	def test_number_of_retries_available_only_with_the_attempts(self):
		panel = self.createPanel()
		self.assertTrue(panel._retriesCountSpin.IsEnabled())
		panel._reinitChk.click(False)
		self.assertFalse(panel._retriesCountSpin.IsEnabled())
		panel._reinitChk.click(True)
		self.assertTrue(panel._retriesCountSpin.IsEnabled())

	def test_number_of_retries_disabled_when_the_attempts_are_off(self):
		options["reinit"] = False
		self.assertFalse(self.createPanel()._retriesCountSpin.IsEnabled())

	def test_limits_of_the_number_of_retries_as_in_the_configuration(self):
		spin = self.createPanel()._retriesCountSpin
		self.assertIn(f"min={spin.min},max={spin.max}", configuration.confspec["retries"])


class TestShortcuts(PanelTestCase):
	def test_every_setting_has_one_shortcut(self):
		self.createPanel()
		for label in controls.labels:
			self.assertEqual(label.count("&"), 0 if label in GROUPS else 1, label)

	def test_shortcuts_are_unique_in_the_settings_dialog(self):
		self.createPanel()
		shortcuts = [shortcut(label) for label in controls.labels if label not in GROUPS]
		self.assertEqual(len(set(shortcuts)), len(shortcuts), shortcuts)
		self.assertFalse(NVDA_SHORTCUTS & set(shortcuts))


class TestConfiguration(AddonTestCase):
	def test_name_and_summary_of_the_addon(self):
		self.assertEqual(
			(configuration.ADDON_NAME, configuration.ADDON_SUMMARY), ("unmute", "Unmute Windows audio"),
		)

	def test_defaults_of_the_options(self):
		defaults = {
			key: re.search(r"default=(\w+)", spec).group(1) for key, spec in configuration.confspec.items()
		}
		self.assertEqual(
			defaults,
			{
				"startup": "true",
				"volume": "20",
				"minlevel": "5",
				"switchdevice": "true",
				"devicechannels": "false",
				"channels": "false",
				"synthvolume": "true",
				"soundsvolume": "true",
				"speechmode": "true",
				"noducking": "false",
				"reinit": "true",
				"retries": "0",
				"playsound": "true",
				"gestures": "false",
			},
		)

	def test_section_is_created_in_the_base_profile(self):
		configuration.saveAddonConfig({"volume": 50})
		self.assertEqual(conf.profiles[0]["unmute"], {"volume": 50})

	def test_sound_split(self):
		self.assertFalse(configuration.isSoundSplitEnabled())
		for state in (1, 2, 6):
			audio["soundSplitState"] = state
			self.assertTrue(configuration.isSoundSplitEnabled(), state)
