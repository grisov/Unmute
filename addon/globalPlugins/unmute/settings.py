#settings.py
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

import addonHandler
from logHandler import log
try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to initialise translations. This may be because the addon is running from NVDA scratchpad.")

import gui
from gui import guiHelper, nvdaControls
import wx
import config
from . import _addonName, _addonSummary


class UnmuteSettingsPanel(gui.SettingsPanel):
	"""Add-on settings panel object"""
	title = _addonSummary

	def __init__(self, parent):
		"""Initializing the add-on settings panel object"""
		super(UnmuteSettingsPanel, self).__init__(parent)

	def makeSettings(self, sizer: wx._core.BoxSizer):
		"""Populate the panel with settings controls.
		@param sizer: The sizer to which to add the settings controls.
		@type sizer: wx._core.BoxSizer
		"""
		self.sizer = sizer
		# Translators: Help message for a dialog.
		helpLabel = wx.StaticText(self, label=_("Select the initial sound system settings that will be set when NVDA starts:"), style=wx.ALIGN_LEFT)
		helpLabel.Wrap(helpLabel.GetSize()[0])
		sizer.Add(helpLabel, flag=wx.EXPAND)

		soundSizer = wx.BoxSizer(wx.VERTICAL)
		# Translators: A setting in addon settings dialog.
		self._customVolumeSlider = guiHelper.LabeledControlHelper(self, _("Set &custom volume level:"), nvdaControls.EnhancedInputSlider,
			value=config.conf[_addonName]['volume'], minValue=0, maxValue=100, size=(250, -1)).control
		soundSizer.Add(self._customVolumeSlider)

		# Translators: A setting in addon settings dialog.
		self._minVolumeSlider = guiHelper.LabeledControlHelper(self, _("Increase the volume if it is &lower than:"), nvdaControls.EnhancedInputSlider,
			value=config.conf[_addonName]['minlevel'], minValue=0, maxValue=100, size=(250, -1)).control
		soundSizer.Add(self._minVolumeSlider)
		sizer.Add(soundSizer, flag=wx.EXPAND)

		driverSizer = wx.BoxSizer(wx.VERTICAL)
		# Translators: A setting in addon settings dialog.
		self._driverChk = wx.CheckBox(self, label=_("&Repeat attempts to initialize the voice synthesizer driver"))
		driverSizer.Add(self._driverChk)
		self._driverChk.SetValue(config.conf[_addonName]['reinit'])

		# Translators: A setting in addon settings dialog.
		self._retriesCountSpin = guiHelper.LabeledControlHelper(self, _("&Number of retries (0 - infinitely):"), nvdaControls.SelectOnFocusSpinCtrl,
			value=str(config.conf[_addonName]['retries']), min=0, max=10000000).control
		driverSizer.Add(self._retriesCountSpin)
		self._retriesCountSpin.Show(self._driverChk.GetValue())
		self._driverChk.Bind(wx.EVT_CHECKBOX, self.onDriverChk)
		sizer.Add(driverSizer, flag=wx.EXPAND)
		self.sizer.Fit(self)

		# Translators: A setting in addon settings dialog.
		self._playSoundChk = wx.CheckBox(self, label=_("Play &sound when audio has been successfully turned on"))
		sizer.Add(self._playSoundChk, flag=wx.EXPAND)
		self._playSoundChk.SetValue(config.conf[_addonName]['playsound'])
		sizer.Fit(self)

	def onDriverChk(self, event) -> None:
		"""Performed when a "self._driverChk" check box is selected or removed.
		@param event: event binder object which processes changing of the wx.Checkbox
		@type event: wx.core.PyEventBinder
		"""
		self._retriesCountSpin.Show(self._driverChk.GetValue())
		self._retriesCountSpin.GetParent().Layout()
		self.sizer.Fit(self)

	def postInit(self):
		"""Set system focus to source language selection dropdown list."""
		self._customVolumeSlider.SetFocus()

	def onSave(self):
		"""Update Configuration when clicking OK."""
		config.conf[_addonName]['volume'] = self._customVolumeSlider.GetValue()
		config.conf[_addonName]['minlevel'] = self._minVolumeSlider.GetValue()
		config.conf[_addonName]['reinit'] = self._driverChk.GetValue()
		config.conf[_addonName]['retries'] = self._retriesCountSpin.GetValue()
		config.conf[_addonName]['playsound'] = self._playSoundChk.GetValue()
