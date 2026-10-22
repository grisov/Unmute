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
		"""Populate the panel with settings controls.

		:param sizer: The sizer to which to add the settings controls.
		"""
		# BoxSizerHelper works with any window, NVDA annotates its parent as a dialog
		addonHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)  # pyright: ignore[reportArgumentType]
		self._startupChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog: everything set below is done when NVDA starts
			# (the sound of Windows and NVDA, the synthesizer), otherwise only with the command of the add-on
			wx.CheckBox(self, label=_("&Unmute when NVDA starts")),
		)
		self._startupChk.SetValue(getAddonConfig()["startup"])
		addonHelper.addItem(
			wx.StaticText(
				self,
				# Translators: Help message for a dialog.
				label=_("Select the initial sound system settings that will be set when NVDA starts:"),
				style=wx.ALIGN_LEFT,
			),
		)
		self._customVolumeSlider = addonHelper.addLabeledControl(
			# Translators: A setting in addon settings dialog.
			_("Set custom &volume level:"),
			nvdaControls.EnhancedInputSlider,
			value=getAddonConfig()["volume"],
			minValue=0,
			maxValue=100,
			size=(250, -1),
		)
		self._minVolumeSlider = addonHelper.addLabeledControl(
			# Translators: A setting in addon settings dialog.
			_("Increase the volume if it is &lower than:"),
			nvdaControls.EnhancedInputSlider,
			value=getAddonConfig()["minlevel"],
			minValue=0,
			maxValue=100,
			size=(250, -1),
		)
		self._channelsChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog: the channels of NVDA are restored when NVDA starts
			# if any of them is muted or lower than the minimum volume level. It is not available
			# while NVDA sound split is enabled, because sound split sets the channels itself
			wx.CheckBox(self, label=_("Turn on the muted c&hannels of NVDA")),
		)
		self._channelsChk.SetValue(getAddonConfig()["channels"])
		self._channelsChk.Enable(not isSoundSplitEnabled())
		self._synthVolumeChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog: the volume of the voice of the synthesizer
			# is raised to the custom volume level if it is lower than the minimum level
			wx.CheckBox(self, label=_("Turn up the volume of the s&ynthesizer voice")),
		)
		self._synthVolumeChk.SetValue(getAddonConfig()["synthvolume"])
		self._soundsVolumeChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog: the volume of the sounds of NVDA is raised to the custom
			# volume level if it is lower than the minimum level. It is not available while the volume of the sounds
			# follows the voice in the NVDA settings, because NVDA has no separate volume of its sounds then
			wx.CheckBox(self, label=_("&Turn up the volume of NVDA sounds")),
		)
		self._soundsVolumeChk.SetValue(getAddonConfig()["soundsvolume"])
		self._soundsVolumeChk.Enable(not isSoundVolumeFollowingVoice())
		self._speechModeChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog: the speech mode of NVDA (NVDA+S) is switched
			# to talk if speech is off, replaced by beeps or on demand
			wx.CheckBox(self, label=_("Switch the speech &mode of NVDA to talk")),
		)
		self._speechModeChk.SetValue(getAddonConfig()["speechmode"])
		self._driverChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog.
			wx.CheckBox(self, label=_("&Repeat attempts to initialize the voice synthesizer driver")),
		)
		self._driverChk.SetValue(getAddonConfig()["reinit"])
		self._retriesCountSpin = addonHelper.addLabeledControl(
			# Translators: A setting in addon settings dialog.
			_("&Number of retries (0 - infinitely):"),
			nvdaControls.SelectOnFocusSpinCtrl,
			value=str(getAddonConfig()["retries"]),
			min=0,
			max=10000000,
		)
		# Disabled instead of hidden: when a labeled control is shown or hidden, NVDA sets the text of its label
		# without the "&" sign, so the shortcut of the label stops working
		self._retriesCountSpin.Enable(self._driverChk.GetValue())
		self._driverChk.Bind(wx.EVT_CHECKBOX, self.onDriverChk)
		self._switchDeviceChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog.
			wx.CheckBox(self, label=_("Switch to the default audio output &device")),
		)
		self._switchDeviceChk.SetValue(getAddonConfig()["switchdevice"])
		self._playSoundChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog.
			wx.CheckBox(self, label=_("Play &sound when audio has been successfully turned on")),
		)
		self._playSoundChk.SetValue(getAddonConfig()["playsound"])
		self._gesturesChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog: the predefined keyboard shortcut of the command
			# that turns on the sound of Windows and NVDA, another one can be assigned in the Input gestures dialog
			wx.CheckBox(self, label=_("Use the default &keyboard shortcut")),
		)
		self._gesturesChk.SetValue(getAddonConfig()["gestures"])

	def onDriverChk(self, event: wx.PyEvent) -> None:
		"""Performed when a "self._driverChk" check box is selected or removed:
		the number of retries is available only when the attempts are repeated.

		:param event: event binder object which processes changing of the wx.Checkbox
		"""
		self._retriesCountSpin.Enable(self._driverChk.GetValue())

	@override
	def onSave(self) -> None:
		"""Update Configuration when clicking OK.
		Add-on parameters are always stored in the basic configuration profile.
		"""
		options: dict[str, Any] = {
			"startup": self._startupChk.GetValue(),
			"volume": self._customVolumeSlider.GetValue(),
			"minlevel": self._minVolumeSlider.GetValue(),
			"channels": self._channelsChk.GetValue(),
			"synthvolume": self._synthVolumeChk.GetValue(),
			"soundsvolume": self._soundsVolumeChk.GetValue(),
			"speechmode": self._speechModeChk.GetValue(),
			"reinit": self._driverChk.GetValue(),
			"retries": self._retriesCountSpin.GetValue(),
			"switchdevice": self._switchDeviceChk.GetValue(),
			"playsound": self._playSoundChk.GetValue(),
			"gestures": self._gesturesChk.GetValue(),
		}
		saveAddonConfig(options)
		# The default gesture is bound or unbound at once
		optionsSaved.notify()
