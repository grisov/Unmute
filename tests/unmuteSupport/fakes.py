# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""Fake audio devices, audio sessions and volume interfaces of Windows Core Audio: the tests never touch real audio.
The fakes answer QueryInterface() only for the interfaces of pycaw the add-on must ask for,
so a wrong interface or a wrong interface ID fails the test.
"""

from __future__ import annotations
import struct
from typing import Any

from comtypes import COMError
from pycaw.api.audioclient import IChannelAudioVolume, ISimpleAudioVolume
from pycaw.api.audiopolicy import IAudioSessionControl2, IAudioSessionManager2
from pycaw.api.endpointvolume import IAudioEndpointVolume
from pycaw.constants import DEVICE_STATE
from pycaw.utils import EDataFlow, ERole

# E_NOTFOUND: the error of a disconnected device or a closed session
E_NOTFOUND = -2147023728


def float32(value: float) -> float:
	"""The value as Windows stores volume levels: a 32-bit float, e.g. 0.29 is read back as 0.28999999."""
	return struct.unpack("f", struct.pack("f", value))[0]


def comError() -> COMError:
	"""The error of a disconnected device or a closed session."""
	return COMError(E_NOTFOUND, "Element not found", None)


class Breakable:
	"""A COM object that raises COMError on every call after it has been broken, e.g. a removed device."""

	broken: bool = False

	def _check(self) -> None:
		if self.broken:
			raise comError()


class FakeEndpointVolume(Breakable):
	"""IAudioEndpointVolume of an audio device, every channel at the level of the device."""

	def __init__(self, level: float = 0.5, channels: int = 2, mute: int = 0) -> None:
		self.level, self.mute = float32(level), mute
		self.channels = [float32(level)] * channels

	def GetMasterVolumeLevelScalar(self) -> float:
		self._check()
		return self.level

	def SetMasterVolumeLevelScalar(self, level: float, context: object) -> None:
		self._check()
		self.level = float32(level)

	def GetChannelCount(self) -> int:
		self._check()
		return len(self.channels)

	def GetChannelVolumeLevelScalar(self, channel: int) -> float:
		self._check()
		return self.channels[channel]

	def SetChannelVolumeLevelScalar(self, channel: int, level: float, context: object) -> None:
		self._check()
		self.channels[channel] = float32(level)

	def GetMute(self) -> int:
		self._check()
		return self.mute

	def SetMute(self, mute: int, context: object) -> None:
		self._check()
		self.mute = int(mute)


class FakeSimpleVolume(Breakable):
	"""ISimpleAudioVolume of an audio session."""

	def __init__(self, level: float = 1.0, mute: int = 0) -> None:
		self.level, self.mute = float32(level), mute

	def GetMasterVolume(self) -> float:
		self._check()
		return self.level

	def SetMasterVolume(self, level: float, context: object) -> None:
		self._check()
		self.level = float32(level)

	def GetMute(self) -> int:
		self._check()
		return self.mute

	def SetMute(self, mute: int, context: object) -> None:
		self._check()
		self.mute = int(mute)


class FakeChannelVolume(Breakable):
	"""IChannelAudioVolume of an audio session."""

	def __init__(self, levels: list[float] | None = None) -> None:
		self.levels = [float32(level) for level in levels or [1.0, 1.0]]

	def GetChannelCount(self) -> int:
		self._check()
		return len(self.levels)

	def GetChannelVolume(self, channel: int) -> float:
		self._check()
		return self.levels[channel]

	def SetChannelVolume(self, channel: int, level: float, context: object) -> None:
		self._check()
		self.levels[channel] = float32(level)


class FakeSession(Breakable):
	"""IAudioSessionControl of an audio session of a program, and its other interfaces."""

	def __init__(
		self,
		pid: int,
		level: float = 1.0,
		mute: int = 0,
		channels: list[float] | None = None,
	) -> None:
		self.pid = pid
		self.volume = FakeSimpleVolume(level, mute)
		self.channels = FakeChannelVolume(channels)
		# The last ducking preference set by the add-on, None if it has not been set
		self.optOut: int | None = None
		# Whether only the process ID cannot be read
		self.noProcess = False

	def QueryInterface(self, interface: Any) -> Any:
		self._check()
		answers = {
			IAudioSessionControl2: self,
			ISimpleAudioVolume: self.volume,
			IChannelAudioVolume: self.channels,
		}
		if interface not in answers:
			raise AssertionError(f"Unexpected interface of an audio session: {interface}")
		return answers[interface]

	def GetProcessId(self) -> int:
		self._check()
		if self.noProcess:
			raise comError()
		return self.pid

	def SetDuckingPreferences(self, optOut: int) -> None:
		self._check()
		self.optOut = optOut


class _Activated:
	"""The object returned by IMMDevice.Activate() for one interface ID."""

	def __init__(self, device: FakeDevice, iid: Any) -> None:
		self.device, self.iid = device, iid

	def QueryInterface(self, interface: Any) -> Any:
		# _iid_ is the way of comtypes to get the ID of an interface
		if self.iid != interface._iid_:
			raise AssertionError(f"Activated {self.iid}, but queried {interface}")
		if interface is IAudioEndpointVolume:
			return self.device.volume
		if interface is IAudioSessionManager2:
			return _SessionManager(self.device)
		raise AssertionError(f"Unexpected interface of an audio device: {interface}")


class _SessionEnumerator:
	def __init__(self, sessions: list[FakeSession | None]) -> None:
		self.sessions = sessions

	def GetCount(self) -> int:
		return len(self.sessions)

	def GetSession(self, index: int) -> FakeSession | None:
		return self.sessions[index]


class _SessionManager:
	def __init__(self, device: FakeDevice) -> None:
		self.device = device

	def GetSessionEnumerator(self) -> _SessionEnumerator:
		self.device._check()
		return _SessionEnumerator(list(self.device.sessions))


class FakeDevice(Breakable):
	"""IMMDevice: an audio output device with its volume and the audio sessions of programs."""

	def __init__(self, id: str, level: float = 0.5, channels: int = 2, mute: int = 0) -> None:
		self.id = id
		self.volume = FakeEndpointVolume(level, channels, mute)
		self.sessions: list[FakeSession | None] = []

	def GetId(self) -> str:
		self._check()
		return self.id

	def Activate(self, iid: Any, clsctx: int, params: None) -> _Activated:
		self._check()
		return _Activated(self, iid)

	def breakDown(self) -> None:
		"""The device has been removed: it and its volume raise COMError."""
		self.broken = self.volume.broken = True


class _DeviceCollection:
	def __init__(self, devices: list[FakeDevice]) -> None:
		self.devices = devices
		# Indexes of the devices removed while the devices are listed
		self.removed: set[int] = set()

	def GetCount(self) -> int:
		return len(self.devices)

	def Item(self, index: int) -> FakeDevice:
		if index in self.removed:
			raise comError()
		return self.devices[index]


class FakeEnumerator:
	"""IMMDeviceEnumerator of the fake audio world of a test, see AudioWorld."""

	def __init__(self, world: AudioWorld) -> None:
		self.world = world

	def GetDefaultAudioEndpoint(self, flow: int, role: int) -> FakeDevice:
		if (flow, role) != (EDataFlow.eRender.value, ERole.eMultimedia.value):
			raise AssertionError(f"Unexpected default device: flow {flow}, role {role}")
		default = self.world.default
		if default is None:
			# E_NOTFOUND: there is no default output device
			raise comError()
		return default

	def GetDevice(self, id: str) -> FakeDevice:
		for device in self.world.devices:
			if device.id == id:
				return device
		raise comError()

	def EnumAudioEndpoints(self, flow: int, stateMask: int) -> _DeviceCollection:
		if (flow, stateMask) != (EDataFlow.eRender.value, DEVICE_STATE.ACTIVE.value):
			raise AssertionError(f"Unexpected devices: flow {flow}, state {stateMask}")
		collection = _DeviceCollection(list(self.world.devices))
		collection.removed = set(self.world.removedWhileListed)
		return collection


class AudioWorld:
	"""The audio devices of Windows in a test: the active output devices, the first one is the default."""

	def __init__(self) -> None:
		self.devices: list[FakeDevice] = []
		# None when the default device is not the first one, e.g. there is no default device
		self.defaultIndex: int | None = 0
		# Whether the audio service of Windows is not available, e.g. it is still starting after logging on
		self.serviceDown = False
		# Indexes of the devices removed while the devices are listed
		self.removedWhileListed: set[int] = set()

	@property
	def default(self) -> FakeDevice | None:
		if self.defaultIndex is None or self.defaultIndex >= len(self.devices):
			return None
		return self.devices[self.defaultIndex]

	def add(self, id: str, level: float = 0.5, channels: int = 2, mute: int = 0) -> FakeDevice:
		"""Add an active output device."""
		device = FakeDevice(id, level, channels, mute)
		self.devices.append(device)
		return device

	def enumerator(self) -> FakeEnumerator:
		"""Stands for AudioUtilities.GetDeviceEnumerator()."""
		if self.serviceDown:
			raise comError()
		return FakeEnumerator(self)
