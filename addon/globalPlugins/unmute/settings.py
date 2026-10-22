# settings.py
# Add-on settings panel
# A part of the NVDA Unmute add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

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

from .configuration import ADDON_SUMMARY, getAddonConfig, saveAddonConfig

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")
_: Callable[[str], str]


class UnmuteSettingsPanel(SettingsPanel):
	"""Add-on settings panel object"""

	title: str = ADDON_SUMMARY

	def __init__(self, parent: wx.Window) -> None:
		"""Initializing the add-on settings panel object.

		:param parent: parent top level window
		"""
		super().__init__(parent)

	@override
	def makeSettings(self, sizer: wx.BoxSizer) -> None:
		"""Populate the panel with settings controls.

		:param sizer: The sizer to which to add the settings controls.
		"""
		# BoxSizerHelper works with any window, NVDA annotates its parent as a dialog
		addonHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)  # pyright: ignore[reportArgumentType]
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
			_("Set &custom volume level:"),
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

	def onDriverChk(self, event: wx.PyEvent) -> None:
		"""Performed when a "self._driverChk" check box is selected or removed:
		the number of retries is available only when the attempts are repeated.

		:param event: event binder object which processes changing of the wx.Checkbox
		"""
		self._retriesCountSpin.Enable(self._driverChk.GetValue())

	def postInit(self) -> None:
		"""Set system focus to the first component in the settings panel."""
		self._customVolumeSlider.SetFocus()

	@override
	def onSave(self) -> None:
		"""Update Configuration when clicking OK.
		Add-on parameters are always stored in the basic configuration profile.
		"""
		options: dict[str, Any] = {
			"volume": self._customVolumeSlider.GetValue(),
			"minlevel": self._minVolumeSlider.GetValue(),
			"reinit": self._driverChk.GetValue(),
			"retries": self._retriesCountSpin.GetValue(),
			"switchdevice": self._switchDeviceChk.GetValue(),
			"playsound": self._playSoundChk.GetValue(),
		}
		saveAddonConfig(options)
