# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""The settings panel of the add-on in the NVDA settings dialog."""

# wxPython has incomplete type annotations and the GUI helpers of NVDA have none, so the types returned
# by most GUI calls in this file are unknown to the type checker, and many wx methods return values
# that are not needed here (e.g. whether a control has been enabled). Only these rules are relaxed for this file.
# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false
# pyright: reportUnusedCallResult=false

from collections.abc import Callable
from typing import Any, override

import addonHandler
import wx
from gui import guiHelper, nvdaControls
from gui.settingsDialogs import SettingsPanel
from logHandler import log

from .configuration import (
	ADDON_SUMMARY,
	getAddonConfig,
	isSoundSplitEnabled,
	isSoundVolumeFollowingVoice,
	optionsSaved,
	saveAddonConfig,
)

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")
_: Callable[[str], str]


class UnmuteSettingsPanel(SettingsPanel):
	"""The settings of the add-on, saved in the base configuration profile of NVDA."""

	title: str = ADDON_SUMMARY

	@override
	def makeSettings(self, sizer: wx.BoxSizer) -> None:
		"""Populate the panel with settings controls, grouped by what they turn on.

		:param sizer: The sizer to which to add the settings controls.
		"""
		# BoxSizerHelper works with any window, NVDA annotates its parent as a dialog
		addonHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)  # pyright: ignore[reportArgumentType]
		self._startupChk = addonHelper.addItem(
			# Translators: A setting: do the checks below when NVDA starts, otherwise only with the command
			wx.CheckBox(self, label=_("&Unmute when NVDA starts")),
		)
		self._startupChk.SetValue(getAddonConfig()["startup"])

		# Translators: The name of a group of settings: the volume levels
		volumeGroup = self._addGroup(addonHelper, _("Volume"))[0]
		self._customVolumeSlider = volumeGroup.addLabeledControl(
			# Translators: A setting in the add-on settings
			_("Set custom &volume level:"),
			nvdaControls.EnhancedInputSlider,
			value=getAddonConfig()["volume"],
			minValue=0,
			maxValue=100,
			size=(250, -1),
		)
		self._minVolumeSlider = volumeGroup.addLabeledControl(
			# Translators: A setting in the add-on settings
			_("Increase the volume if it is &lower than:"),
			nvdaControls.EnhancedInputSlider,
			value=getAddonConfig()["minlevel"],
			minValue=0,
			maxValue=100,
			size=(250, -1),
		)

		# Translators: The name of a group of settings: the audio devices of Windows
		devicesGroup, devicesBox = self._addGroup(addonHelper, _("Windows audio devices"))
		self._switchDeviceChk = devicesGroup.addItem(
			# Translators: A setting in the add-on settings
			wx.CheckBox(devicesBox, label=_("Switch to the default audio output &device")),
		)
		self._switchDeviceChk.SetValue(getAddonConfig()["switchdevice"])
		self._deviceChannelsChk = devicesGroup.addItem(
			# Translators: A setting: raise each muted channel of the audio devices
			wx.CheckBox(devicesBox, label=_("Turn on the muted channels of audio d&evices")),
		)
		self._deviceChannelsChk.SetValue(getAddonConfig()["devicechannels"])

		# Translators: The name of a group of settings: the settings of NVDA itself
		screenReaderGroup, screenReaderBox = self._addGroup(addonHelper, _("Screen reader"))
		self._channelsChk = screenReaderGroup.addItem(
			# Translators: A setting, not available while NVDA sound split is enabled
			wx.CheckBox(screenReaderBox, label=_("Turn on the muted c&hannels of NVDA")),
		)
		self._channelsChk.SetValue(getAddonConfig()["channels"])
		self._channelsChk.Enable(not isSoundSplitEnabled())
		self._synthVolumeChk = screenReaderGroup.addItem(
			# Translators: A setting: raise the too quiet voice of the synthesizer
			wx.CheckBox(screenReaderBox, label=_("Turn up the volume of the s&ynthesizer voice")),
		)
		self._synthVolumeChk.SetValue(getAddonConfig()["synthvolume"])
		self._soundsVolumeChk = screenReaderGroup.addItem(
			# Translators: A setting, not available while the volume of NVDA sounds follows the voice
			wx.CheckBox(screenReaderBox, label=_("&Turn up the volume of NVDA sounds")),
		)
		self._soundsVolumeChk.SetValue(getAddonConfig()["soundsvolume"])
		self._soundsVolumeChk.Enable(not isSoundVolumeFollowingVoice())
		self._speechModeChk = screenReaderGroup.addItem(
			# Translators: A setting: switch the speech mode of NVDA (NVDA+S) to talk
			wx.CheckBox(screenReaderBox, label=_("Switch the speech &mode of NVDA to talk")),
		)
		self._speechModeChk.SetValue(getAddonConfig()["speechmode"])
		self._noDuckingChk = screenReaderGroup.addItem(
			# Translators: A setting: keep the volume of NVDA when Windows lowers other sounds during calls
			wx.CheckBox(screenReaderBox, label=_("Do not lo&wer the volume of NVDA during calls")),
		)
		self._noDuckingChk.SetValue(getAddonConfig()["noducking"])
		self._reinitChk = screenReaderGroup.addItem(
			wx.CheckBox(
				screenReaderBox,
				# Translators: A setting in the add-on settings
				label=_("&Repeat attempts to initialize the voice synthesizer driver"),
			),
		)
		self._reinitChk.SetValue(getAddonConfig()["reinit"])
		self._retriesCountSpin = screenReaderGroup.addLabeledControl(
			# Translators: A setting in the add-on settings
			_("&Number of retries (0 - infinitely):"),
			nvdaControls.SelectOnFocusSpinCtrl,
			value=str(getAddonConfig()["retries"]),
			min=0,
			max=10000000,
		)
		# Disabled instead of hidden: when a labeled control is shown or hidden, NVDA sets the text of its label
		# without the "&" sign, so the shortcut of the label stops working
		self._retriesCountSpin.Enable(self._reinitChk.GetValue())
		self._reinitChk.Bind(wx.EVT_CHECKBOX, self.onReinitChk)

		self._playSoundChk = addonHelper.addItem(
			# Translators: A setting in the add-on settings
			wx.CheckBox(self, label=_("Play &sound when audio has been successfully turned on")),
		)
		self._playSoundChk.SetValue(getAddonConfig()["playsound"])
		self._gesturesChk = addonHelper.addItem(
			# Translators: A setting: bind the predefined keyboard shortcut of the command
			wx.CheckBox(self, label=_("Use the default &keyboard shortcut")),
		)
		self._gesturesChk.SetValue(getAddonConfig()["gestures"])

	def _addGroup(
		self,
		helper: guiHelper.BoxSizerHelper,
		label: str,
	) -> tuple[guiHelper.BoxSizerHelper, wx.StaticBox]:
		"""Add a named group of settings to the panel, as NVDA groups its settings.
		The controls of the group must be created with its box as the parent, so a screen reader announces the group.

		:param helper: the helper of the panel
		:param label: the name of the group
		:return: the helper to add the controls of the group and the box of the group
		"""
		groupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=label)
		# BoxSizerHelper works with any window, NVDA annotates its parent as a dialog
		group = guiHelper.BoxSizerHelper(self, sizer=groupSizer)  # pyright: ignore[reportArgumentType]
		helper.addItem(group)
		return group, groupSizer.GetStaticBox()

	def onReinitChk(self, event: wx.PyEvent) -> None:
		"""Performed when the check box of the attempts to initialize the synthesizer is checked or unchecked:
		the number of retries is available only when the attempts are repeated.

		:param event: event binder object which processes changing of the wx.Checkbox
		"""
		self._retriesCountSpin.Enable(self._reinitChk.GetValue())

	@override
	def onSave(self) -> None:
		"""Update Configuration when clicking OK.
		Add-on parameters are always stored in the basic configuration profile.
		"""
		options: dict[str, Any] = {
			"startup": self._startupChk.GetValue(),
			"volume": self._customVolumeSlider.GetValue(),
			"minlevel": self._minVolumeSlider.GetValue(),
			"devicechannels": self._deviceChannelsChk.GetValue(),
			"channels": self._channelsChk.GetValue(),
			"synthvolume": self._synthVolumeChk.GetValue(),
			"soundsvolume": self._soundsVolumeChk.GetValue(),
			"speechmode": self._speechModeChk.GetValue(),
			"noducking": self._noDuckingChk.GetValue(),
			"reinit": self._reinitChk.GetValue(),
			"retries": self._retriesCountSpin.GetValue(),
			"switchdevice": self._switchDeviceChk.GetValue(),
			"playsound": self._playSoundChk.GetValue(),
			"gestures": self._gesturesChk.GetValue(),
		}
		saveAddonConfig(options)
		# The default gesture and the ducking preference are applied at once
		optionsSaved.notify()
