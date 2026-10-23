# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""The Ukrainian translation: every string of the settings panel is translated with a unique keyboard shortcut."""

import ast
import re

from unmuteSupport import ADDON_DIR, controls, module
from unmuteSupport.case import AddonTestCase

PO_FILE = ADDON_DIR.parents[1] / "locale" / "uk" / "LC_MESSAGES" / "nvda.po"
# The keyboard shortcuts of the NVDA settings dialog in Ukrainian: &Категорії, &Гаразд, &Скасувати, &Застосувати
NVDA_SHORTCUTS = {"к", "г", "с", "з"}


def readCatalog(path):
	"""Read the translations of a .po file.

	:return: the translations by their English strings, without the header; fuzzy translations are empty
	"""
	catalog = {}
	for entry in path.read_text(encoding="utf-8").split("\n\n"):
		fuzzy = "#, fuzzy" in entry
		texts = {"msgid": "", "msgstr": ""}
		key = None
		for line in entry.splitlines():
			match = re.match(r"(msgid|msgstr) (\".*\")$", line)
			if match:
				key = match.group(1)
				texts[key] = ast.literal_eval(match.group(2))
			elif line.startswith('"') and key:
				texts[key] += ast.literal_eval(line)
		if texts["msgid"]:
			catalog[texts["msgid"]] = "" if fuzzy else texts["msgstr"]
	return catalog


class TestUkrainian(AddonTestCase):
	def setUp(self):
		super().setUp()
		self.catalog = readCatalog(PO_FILE)
		controls.labels.clear()
		module("settings").UnmuteSettingsPanel().makeSettings(None)
		self.labels = list(controls.labels)

	def test_every_string_is_translated(self):
		self.assertEqual([text for text, translation in self.catalog.items() if not translation], [])

	def test_strings_of_the_panel_are_in_the_translation(self):
		self.assertEqual([label for label in self.labels if label not in self.catalog], [])

	def test_every_shortcut_is_kept(self):
		for label in self.labels:
			self.assertEqual(self.catalog[label].count("&"), label.count("&"), self.catalog[label])

	def test_shortcuts_are_unique_in_the_settings_dialog(self):
		shortcuts = [
			match.group(1).lower()
			for label in self.labels
			if (match := re.search(r"&(\w)", self.catalog[label]))
		]
		self.assertEqual(len(set(shortcuts)), len(shortcuts), shortcuts)
		self.assertFalse(NVDA_SHORTCUTS & set(shortcuts))

	def test_only_plain_dashes_in_the_translation(self):
		self.assertEqual([text for text in self.catalog.values() if re.search(r"[\u2013\u2014]", text)], [])
