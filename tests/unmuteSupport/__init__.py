# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""Loads the add-on outside NVDA for the tests of the add-on.

The modules of NVDA are replaced with small stand-ins that record what the add-on does (played sounds,
bound gestures, delayed calls). comtypes and pycaw are the real ones: the tests run only on Windows
and are skipped elsewhere, e.g. in the tests workflow on Linux.
The unit tests never change the volume of real audio devices or programs: they use the fakes of fakes.py.
"""

from __future__ import annotations
import builtins
import enum
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

if sys.platform != "win32":
	raise unittest.SkipTest("the tests of the add-on need Windows, comtypes and pycaw")

ADDON_DIR = Path(__file__).parents[2] / "addon" / "globalPlugins" / "unmute"
PACKAGE = "unmute"

# What the add-on did, inspected by the tests: sounds, restarts of the synthesizer and tones, delayed calls
events: list[Any] = []
# The calls delayed with core.callLater, run by the tests with runLater()
later: list[tuple[int, Any, tuple[Any, ...]]] = []
# The add-on section and the other sections of the NVDA configuration
options: dict[str, Any] = {}
audio: dict[str, Any] = {}
speechConfig: dict[str, Any] = {}


class _Log:
	"""Collects the errors and debug warnings logged by the add-on, so the tests can check them."""

	def __init__(self) -> None:
		self.errors: list[str] = []
		self.warnings: list[str] = []

	def error(self, message: str, *args: Any, **kwargs: Any) -> None:
		self.errors.append(message)

	def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
		self.warnings.append(message % args if args else message)

	def debugWarning(self, message: str, *args: Any, **kwargs: Any) -> None:
		self.warnings.append(message)

	def clear(self) -> None:
		self.errors.clear()
		self.warnings.clear()


log = _Log()


class _Profile(dict[str, Any]):
	"""The base configuration profile of NVDA: the add-on writes its section there."""


class _Conf(dict[str, Any]):
	"""Stands for config.conf: the sections of the active profile, the profiles and the cache of the sections."""

	def __init__(self) -> None:
		super().__init__()
		self.spec: dict[str, Any] = {}
		self.profiles: list[_Profile] = [_Profile()]
		self.rootSection = types.SimpleNamespace(_cache={})

	def __getitem__(self, key: str) -> dict[str, Any]:
		return {PACKAGE: options, "audio": audio, "speech": speechConfig}[key]


conf = _Conf()


class _Action:
	"""Stands for extensionPoints.Action."""

	def __init__(self) -> None:
		self.handlers: list[Any] = []

	def register(self, handler: Any) -> None:
		self.handlers.append(handler)

	def unregister(self, handler: Any) -> bool:
		if handler in self.handlers:
			self.handlers.remove(handler)
			return True
		return False

	def notify(self, **kwargs: Any) -> None:
		for handler in list(self.handlers):
			handler(**kwargs)


class _GlobalPlugin:
	"""Stands for globalPluginHandler.GlobalPlugin: records the bound gestures like ScriptableObject.bindGestures."""

	def __init__(self, *args: Any, **kwargs: Any) -> None:
		self.boundGestures: dict[str, str] = {}

	def bindGestures(self, gestures: dict[str, str | None]) -> None:
		for gesture, scriptName in gestures.items():
			if scriptName:
				self.boundGestures[gesture] = scriptName
			else:
				self.boundGestures.pop(gesture, None)

	def terminate(self) -> None:
		pass


def _script(description: str = "", **kwargs: Any) -> Any:
	"""Stands for scriptHandler.script: the description becomes the docstring, as in NVDA."""

	def decorate(function: Any) -> Any:
		if description:
			function.__doc__ = description
		return function

	return decorate


def _callLater(delay: int, function: Any, *args: Any) -> None:
	"""Stands for core.callLater: keeps the call for runLater() and records the delay among the events."""
	events.append(("later", delay, function.__name__))
	later.append((delay, function, args))


def runLater() -> None:
	"""Run the calls delayed with core.callLater so far, not the ones they delay in turn."""
	pending = list(later)
	later.clear()
	for _delay, function, args in pending:
		function(*args)


class SpeechMode(enum.IntEnum):
	"""speech.SpeechMode of NVDA."""

	off = 0
	beeps = 1
	talk = 2
	onDemand = 3


speechState = types.SimpleNamespace(speechMode=SpeechMode.talk)


def _setSpeechMode(mode: SpeechMode) -> None:
	speechState.speechMode = mode
	events.append(("speechMode", mode.name))


class FakeSynth:
	"""A synthesizer of NVDA with its volume."""

	def __init__(self, name: str = "espeak", volume: int = 100, hasVolume: bool = True) -> None:
		self.name, self.volume, self.hasVolume = name, volume, hasVolume

	def isSupported(self, setting: str) -> bool:
		return setting == "volume" and self.hasVolume


# The synthesizer of NVDA, None if it is not initialized, and whether setSynth succeeds
synth: dict[str, Any] = {"current": None, "starts": True}
# Whether nvwave cannot play a sound
sound: dict[str, bool] = {"fails": False}


def _setSynth(name: str) -> bool:
	events.append(("setSynth", name, audio.get("outputDevice")))
	if synth["starts"]:
		synth["current"] = synth["current"] or FakeSynth(name)
	return synth["starts"]


def _playWaveFile(path: str) -> None:
	if sound["fails"]:
		raise OSError("no audio")
	events.append(("sound", Path(path).name))


synthChanged = _Action()


def _module(name: str, **attributes: Any) -> types.ModuleType:
	module = types.ModuleType(name)
	module.__dict__.update(attributes)
	sys.modules[name] = module
	return module


def _installNvda() -> None:
	"""Replace the modules of NVDA used by the add-on."""
	_module("config", conf=conf)
	_module(
		"addonHandler",
		initTranslation=lambda: None,
		AddonError=Exception,
		getCodeAddon=lambda: types.SimpleNamespace(
			name=PACKAGE, manifest={"summary": "Unmute Windows audio"},
		),
	)
	_module("extensionPoints", Action=_Action)
	_module("logHandler", log=log)
	_module("core", callLater=_callLater)
	_module("globalPluginHandler", GlobalPlugin=_GlobalPlugin)
	_module("scriptHandler", script=_script)
	_module("inputCore", InputGesture=object)
	_module("nvwave", playWaveFile=_playWaveFile)
	_module(
		"tones",
		terminate=lambda: events.append("tones.terminate"),
		initialize=lambda: events.append("tones.initialize"),
	)
	_module(
		"speech",
		SpeechMode=SpeechMode,
		getState=lambda: speechState,
		setSpeechMode=_setSpeechMode,
	)
	_module(
		"synthDriverHandler",
		synthChanged=synthChanged,
		getSynth=lambda: synth["current"],
		setSynth=_setSynth,
	)
	settingsDialogs = _module(
		"gui.settingsDialogs",
		SettingsPanel=type("SettingsPanel", (), {}),
		NVDASettingsDialog=types.SimpleNamespace(categoryClasses=[]),
	)
	from .controls import FakeBoxSizerHelper, FakeCheckBox, FakeSlider, FakeSpin, FakeStaticBoxSizer

	_module("gui", settingsDialogs=settingsDialogs, guiHelper=None, nvdaControls=None)
	sys.modules["gui"].guiHelper = _module("gui.guiHelper", BoxSizerHelper=FakeBoxSizerHelper)
	sys.modules["gui"].nvdaControls = _module(
		"gui.nvdaControls",
		EnhancedInputSlider=FakeSlider,
		SelectOnFocusSpinCtrl=FakeSpin,
	)
	_module(
		"wx",
		CheckBox=FakeCheckBox,
		StaticBoxSizer=FakeStaticBoxSizer,
		StaticBox=object,
		BoxSizer=object,
		PyEvent=object,
		VERTICAL=8,
		EVT_CHECKBOX="EVT_CHECKBOX",
		Window=MagicMock,
	)
	builtins._ = lambda text: text  # type: ignore[attr-defined]


def _load() -> types.ModuleType:
	"""Load the add-on package once, with the stand-ins of NVDA and the real comtypes and pycaw."""
	if PACKAGE in sys.modules and getattr(sys.modules[PACKAGE], "__unmuteTests__", False):
		return sys.modules[PACKAGE]
	_installNvda()
	# No compiled files in the folder of the add-on: they could get into the package of the add-on
	sys.dont_write_bytecode = True
	spec = importlib.util.spec_from_file_location(
		PACKAGE,
		ADDON_DIR / "__init__.py",
		submodule_search_locations=[str(ADDON_DIR)],
	)
	assert spec is not None and spec.loader is not None
	package = importlib.util.module_from_spec(spec)
	sys.modules[PACKAGE] = package
	spec.loader.exec_module(package)
	sys.dont_write_bytecode = False
	package.__unmuteTests__ = True
	return package


addon = _load()


def module(name: str) -> types.ModuleType:
	"""A module of the add-on, e.g. module("audio")."""
	return sys.modules[f"{PACKAGE}.{name}"]
