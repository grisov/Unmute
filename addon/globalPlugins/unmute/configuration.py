# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""The name, the summary and the options of the add-on in the NVDA configuration."""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any, cast

import addonHandler
import config
import extensionPoints

# The manifest of the add-on has no type annotations
_addon = cast(Any, addonHandler).getCodeAddon()
ADDON_NAME: str = _addon.name
ADDON_SUMMARY: str = _addon.manifest["summary"]

# The options of the add-on in the NVDA configuration
confspec: dict[str, str] = {
	# Turn on the sound and initialize the synthesizer when NVDA starts, otherwise only with the command
	"startup": "boolean(default=true)",
	"volume": "integer(default=20,min=0,max=100)",
	"minlevel": "integer(default=5,min=0,max=100)",
	"reinit": "boolean(default=true)",
	"retries": "integer(default=0,min=0,max=10000000)",
	"switchdevice": "boolean(default=true)",
	# Restore the channels of the audio sessions of NVDA if any of them is muted or too quiet
	"channels": "boolean(default=false)",
	# Raise the volume of the voice of the synthesizer if it is lower than the minimum level
	"synthvolume": "boolean(default=true)",
	# Switch the speech mode of NVDA to talk if speech is off, replaced by beeps or on demand
	"speechmode": "boolean(default=true)",
	"playsound": "boolean(default=true)",
	# Bind the default gesture to the command of the add-on
	"gestures": "boolean(default=false)",
}


# Notifies the global plugin that the options of the add-on have been saved in the settings panel
optionsSaved = extensionPoints.Action()


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


def isSoundSplitEnabled() -> bool:
	"""Check whether NVDA sound split is enabled. Any state except "disabled" (0) sets the levels
	of the channels of all audio sessions, NVDA included, so they must not be changed by the add-on then.

	:return: whether sound split of NVDA is enabled
	"""
	return getNvdaConfig("audio")["soundSplitState"] != 0


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
	# NVDA caches the values read through config.conf, and a change of a profile itself does not update the cache:
	# the cached section of the add-on is dropped, so the new values apply at once, without restarting NVDA
	cast(Any, config.conf).rootSection._cache.pop(ADDON_NAME, None)
