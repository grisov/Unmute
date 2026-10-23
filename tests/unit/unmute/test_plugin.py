# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""The global plugin: the checks when NVDA starts, the command, its default gesture and the end of the plugin."""

from unmuteSupport import addon, events, log, module, options, synthChanged
from unmuteSupport.case import AddonTestCase

GESTURE = "kb:NVDA+windows+shift+u"
optionsSaved = module("configuration").optionsSaved


class TestStartup(AddonTestCase):
	def test_checks_when_nvda_starts(self):
		options["startup"] = True
		self.recreatePlugin()
		self.assertEqual(events, [("later", 0, "restoreSoundAndSpeech")])

	def test_only_the_command_without_the_startup_option(self):
		options["reinit"] = True
		self.recreatePlugin()
		self.assertEqual(events, [])

	def test_ducking_preference_does_not_depend_on_the_startup_option(self):
		options["noducking"] = True
		self.recreatePlugin()
		self.assertEqual(events, [("later", 1000, "applyDuckingPreference")])

	def test_options_of_the_addon_are_registered(self):
		from unmuteSupport import conf

		self.assertIs(conf.spec["unmute"], module("configuration").confspec)

	def test_settings_panel_is_registered_once(self):
		self.assertEqual(self.categoryClasses, [module("settings").UnmuteSettingsPanel])


class TestCommand(AddonTestCase):
	def test_description_of_the_command(self):
		self.assertEqual(addon.GlobalPlugin.script_unmute.__doc__, "Turn on the sound of Windows and NVDA")

	def test_category_of_the_command(self):
		self.assertEqual(addon.GlobalPlugin.scriptCategory, "Unmute Windows audio")

	def test_no_default_gesture_after_installation(self):
		self.assertEqual(self.plugin.boundGestures, {})

	def test_default_gesture_with_the_option(self):
		options["gestures"] = True
		self.recreatePlugin()
		self.assertEqual(self.plugin.boundGestures, {GESTURE: "unmute"})

	def test_default_gesture_changes_when_the_settings_are_saved(self):
		options["gestures"] = True
		optionsSaved.notify()
		self.assertEqual(self.plugin.boundGestures, {GESTURE: "unmute"})
		options["gestures"] = False
		optionsSaved.notify()
		self.assertEqual(self.plugin.boundGestures, {})

	def test_ducking_preference_applies_when_the_settings_are_saved(self):
		options["noducking"] = True
		session = self.addSession(self.speakers)
		optionsSaved.notify()
		self.assertEqual(session.optOut, 1)

	def test_command_does_everything_without_the_startup_option(self):
		self.speakers.volume.level = 0.0
		self.plugin.script_unmute(None)
		self.assertGreater(self.speakers.volume.level, 0.0)


class TestTerminate(AddonTestCase):
	def test_handlers_and_panel_are_removed(self):
		self.plugin.terminate()
		self.assertEqual(optionsSaved.handlers, [])
		self.assertEqual(synthChanged.handlers, [])
		self.assertEqual(self.categoryClasses, [])

	def test_panel_already_removed(self):
		self.categoryClasses.clear()
		self.plugin.terminate()
		self.assertEqual(log.errors, [])
		self.assertTrue(any("Settings panel" in warning for warning in log.warnings))
