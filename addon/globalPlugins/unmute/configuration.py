# configuration.py
# The name, the summary and the options of the add-on in the NVDA configuration
# A part of the NVDA Unmute add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any, cast

import addonHandler
import config

# The manifest of the add-on has no type annotations
_addon = cast(Any, addonHandler).getCodeAddon()
ADDON_NAME: str = _addon.name
ADDON_SUMMARY: str = _addon.manifest["summary"]

# The options of the add-on in the NVDA configuration
confspec: dict[str, str] = {
	"volume": "integer(default=20,min=0,max=100)",
	"minlevel": "integer(default=5,min=0,max=100)",
	"reinit": "boolean(default=true)",
	"retries": "integer(default=0,min=0,max=10000000)",
	"switchdevice": "boolean(default=true)",
	"playsound": "boolean(default=true)",
}


def getNvdaConfig(section: str) -> MutableMapping[str, Any]:
	"""Get a section of the NVDA configuration in the current configuration profile.
	NVDA declares config.conf as None until the configuration is loaded, so its type is given here once.

	:param section: the name of the section, e.g. "audio"
	:return: the section of the configuration
	"""
	return cast(Any, config.conf)[section]


def getAddonConfig() -> MutableMapping[str, Any]:
	"""Get the add-on section of the NVDA configuration in the current configuration profile.

	:return: the options of the add-on
	"""
	return getNvdaConfig(ADDON_NAME)


def saveAddonConfig(options: dict[str, Any]) -> None:
	"""Save the options of the add-on in the base configuration profile of NVDA,
	so they apply whatever configuration profile is active.

	:param options: the options of the add-on and their values
	"""
	# The configuration profiles of NVDA have no type annotations
	baseProfile = cast(Any, config.conf).profiles[0]
	try:
		baseProfile[ADDON_NAME].update(options)
	except (KeyError, AttributeError):
		baseProfile[ADDON_NAME] = options
