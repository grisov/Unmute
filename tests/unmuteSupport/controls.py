# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""Stand-ins of the wx controls and the GUI helpers of NVDA used by the settings panel."""

from __future__ import annotations
import types
from typing import Any

# The labels of all controls and groups created by the settings panel, in the order of creation
labels: list[str] = []


class FakeControl:
	"""A control with a value that can be enabled or disabled."""

	def __init__(self, parent: Any = None, value: Any = None, **kwargs: Any) -> None:
		self.parent, self.value, self.enabled = parent, value, True

	def SetValue(self, value: Any) -> None:
		self.value = value

	def GetValue(self) -> Any:
		return self.value

	def Enable(self, enable: bool = True) -> bool:
		self.enabled = bool(enable)
		return True

	def IsEnabled(self) -> bool:
		return self.enabled


class FakeCheckBox(FakeControl):
	"""wx.CheckBox: keeps its label and the handlers bound to it."""

	def __init__(self, parent: Any, label: str = "", **kwargs: Any) -> None:
		super().__init__(parent, False)
		self.label = label
		self.handlers: dict[Any, Any] = {}
		labels.append(label)

	def Bind(self, event: Any, handler: Any) -> None:
		self.handlers[event] = handler

	def click(self, value: bool) -> None:
		"""Check or uncheck the check box as the user does."""
		self.value = value
		for handler in self.handlers.values():
			handler(None)


class FakeSlider(FakeControl):
	"""nvdaControls.EnhancedInputSlider."""


class FakeSpin(FakeControl):
	"""nvdaControls.SelectOnFocusSpinCtrl: the value is given as text and read as a number."""

	def __init__(self, parent: Any = None, value: str = "0", **kwargs: Any) -> None:
		super().__init__(parent, int(value))
		self.min, self.max = kwargs.get("min"), kwargs.get("max")


class FakeStaticBoxSizer:
	"""wx.StaticBoxSizer: a named group of controls."""

	def __init__(self, orient: int, parent: Any, label: str = "") -> None:
		self.box = types.SimpleNamespace(label=label)
		labels.append(label)

	def GetStaticBox(self) -> Any:
		return self.box


class FakeBoxSizerHelper:
	"""gui.guiHelper.BoxSizerHelper: returns the added controls, as the real one does."""

	def __init__(self, parent: Any, sizer: Any = None, **kwargs: Any) -> None:
		self.parent, self.sizer = parent, sizer
		self.items: list[Any] = []

	def addItem(self, item: Any, **kwargs: Any) -> Any:
		self.items.append(item)
		return item

	def addLabeledControl(self, label: str, controlClass: Any, **kwargs: Any) -> Any:
		labels.append(label)
		return self.addItem(controlClass(self.parent, **kwargs))
