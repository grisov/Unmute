# A part of the NVDA Unmute add-on
# Copyright (C) 2020-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""Access to Windows Core Audio: audio devices, their volume and the volume of audio sessions.
Thin functions over the COM interfaces of Windows Core Audio.
The helpers of pycaw 20251023+ such as AudioUtilities.GetSpeakers() and GetAllSessions() wrap every device
with AudioUtilities.CreateDevice(), which reads the whole property store of the device. That is slow,
e.g. for Bluetooth devices, and NVDA logs a warning for each property that cannot be read, so these
functions use the interfaces directly.

comtypes creates the methods of COM interfaces at run time and pycaw has no type annotations,
so the protocols below describe only the methods the add-on uses.
"""

from __future__ import annotations

from typing import Any, Protocol, cast

from comtypes import CLSCTX_ALL, COMError
from logHandler import log
from pycaw.api.audioclient import IChannelAudioVolume, ISimpleAudioVolume
from pycaw.api.audiopolicy import IAudioSessionControl2, IAudioSessionManager2
from pycaw.api.endpointvolume import IAudioEndpointVolume
from pycaw.constants import DEVICE_STATE
from pycaw.utils import AudioUtilities, EDataFlow, ERole


class EndpointVolume(Protocol):
	"""IAudioEndpointVolume: the volume of an audio device."""

	def GetMasterVolumeLevelScalar(self) -> float: ...

	def SetMasterVolumeLevelScalar(self, level: float, context: object | None) -> None: ...

	def GetChannelCount(self) -> int: ...

	def GetChannelVolumeLevelScalar(self, channel: int) -> float: ...

	def SetChannelVolumeLevelScalar(self, channel: int, level: float, context: object | None) -> None: ...

	def GetMute(self) -> int: ...

	def SetMute(self, mute: int, context: object | None) -> None: ...


class SimpleVolume(Protocol):
	"""ISimpleAudioVolume: the volume of an audio session."""

	def GetMasterVolume(self) -> float: ...

	def SetMasterVolume(self, level: float, context: object | None) -> None: ...

	def GetMute(self) -> int: ...

	def SetMute(self, mute: int, context: object | None) -> None: ...


class ChannelVolume(Protocol):
	"""IChannelAudioVolume: the volume of the channels of an audio session, relative to the volume of the session."""

	def GetChannelCount(self) -> int: ...

	def GetChannelVolume(self, channel: int) -> float: ...

	def SetChannelVolume(self, channel: int, level: float, context: object | None) -> None: ...


class Device(Protocol):
	"""IMMDevice: an audio device."""

	def GetId(self) -> str: ...

	def Activate(self, iid: Any, clsctx: int, params: None) -> Any: ...


class DeviceCollection(Protocol):
	"""IMMDeviceCollection: a list of audio devices."""

	def GetCount(self) -> int: ...

	def Item(self, index: int) -> Device: ...


class DeviceEnumerator(Protocol):
	"""IMMDeviceEnumerator: lists the audio devices."""

	def EnumAudioEndpoints(self, flow: int, stateMask: int) -> DeviceCollection: ...

	def GetDefaultAudioEndpoint(self, flow: int, role: int) -> Device: ...

	def GetDevice(self, id: str) -> Device: ...


class Session(Protocol):
	"""IAudioSessionControl2: an audio session of a running program."""

	def GetProcessId(self) -> int: ...

	def QueryInterface(self, interface: Any) -> Any: ...


class SessionEnumerator(Protocol):
	"""IAudioSessionEnumerator: the audio sessions of an audio device."""

	def GetCount(self) -> int: ...

	def GetSession(self, index: int) -> Any: ...


class SessionManager(Protocol):
	"""IAudioSessionManager2: the audio sessions of an audio device."""

	def GetSessionEnumerator(self) -> SessionEnumerator: ...


def logDebugWarning(message: str) -> None:
	"""Log a debug warning with the exception being handled.
	Logger.debugWarning of NVDA has no type annotations, so it is called through this function.

	:param message: the message to log
	"""
	cast(Any, log).debugWarning(message, exc_info=True)


def getDeviceEnumerator() -> DeviceEnumerator:
	"""Get the enumerator of the audio devices.

	:return: the device enumerator
	:raises COMError: the audio service of Windows is not available, e.g. it is still starting
	"""
	return cast(DeviceEnumerator, AudioUtilities.GetDeviceEnumerator())


def getDefaultOutputDevice() -> Device | None:
	"""Get the default output device of Windows for multimedia, the one that plays the sound of most programs.

	:return: the audio device, None if there is no default output device or the audio service is not available
	"""
	try:
		return getDeviceEnumerator().GetDefaultAudioEndpoint(EDataFlow.eRender.value, ERole.eMultimedia.value)
	except COMError:
		logDebugWarning("Unable to get the default output audio device")
		return None


def getDevice(deviceId: str) -> Device | None:
	"""Get the audio device by its ID, e.g. the output device selected in the NVDA settings.

	:param deviceId: the device ID
	:return: the audio device, None if it is not known to Windows or the audio service is not available
	"""
	try:
		return getDeviceEnumerator().GetDevice(deviceId)
	except COMError:
		logDebugWarning(f"Unable to get the audio device {deviceId}")
		return None


def getActiveOutputDevices() -> list[Device]:
	"""Get all active output devices in the order of Windows.
	Disabled, unplugged and not present devices are skipped.

	:return: the output devices, empty if the audio service is not available
	"""
	try:
		collection = getDeviceEnumerator().EnumAudioEndpoints(
			EDataFlow.eRender.value,
			DEVICE_STATE.ACTIVE.value,
		)
		count = collection.GetCount()
	except COMError:
		logDebugWarning("Unable to list the active output audio devices")
		return []
	devices: list[Device] = []
	for i in range(count):
		try:
			devices.append(collection.Item(i))
		except COMError:
			# The device has been removed while the devices were listed
			continue
	return devices


def getDeviceId(device: Device) -> str:
	"""Get the ID of the audio device.

	:param device: audio device
	:return: the device ID, empty if the device is not available anymore
	"""
	try:
		return device.GetId()
	except COMError:
		return ""


def getEndpointVolume(device: Device) -> EndpointVolume:
	"""Get the volume interface of the audio device.
	QueryInterface() adds a COM reference for the new pointer object. ctypes.cast() must not be used here:
	it creates a second pointer object without a reference, so the interface is released twice
	when both objects are discarded, which can crash NVDA.

	:param device: audio device
	:return: the volume interface of the device
	:raises COMError: the device is not available anymore
	"""
	# _iid_ is the way of comtypes to get the ID of an interface
	iid = IAudioEndpointVolume._iid_  # pyright: ignore[reportPrivateUsage]
	return cast(EndpointVolume, device.Activate(iid, CLSCTX_ALL, None).QueryInterface(IAudioEndpointVolume))


def listSessions(device: Device) -> list[Session]:
	"""Get all audio sessions of the audio device, only their control interfaces are queried.
	Unlike AudioUtilities.GetAllSessions(), this works for any device, not only the default one,
	and does not read the properties of the device.

	:param device: audio device
	:return: audio sessions of the device, empty if the device is not available anymore
	"""
	try:
		# _iid_ is the way of comtypes to get the ID of an interface
		iid = IAudioSessionManager2._iid_  # pyright: ignore[reportPrivateUsage]
		manager = cast(
			SessionManager,
			device.Activate(iid, CLSCTX_ALL, None).QueryInterface(IAudioSessionManager2),
		)
		sessionEnumerator = manager.GetSessionEnumerator()
		count = sessionEnumerator.GetCount()
	except COMError:
		logDebugWarning("Unable to get the audio sessions of the audio device")
		return []
	sessions: list[Session] = []
	for i in range(count):
		try:
			control = sessionEnumerator.GetSession(i)
			if control is not None:
				sessions.append(cast(Session, control.QueryInterface(IAudioSessionControl2)))
		except COMError:
			# The session has been closed while the sessions were listed
			continue
	return sessions


def getSessionVolume(session: Session) -> SimpleVolume:
	"""Get the volume interface of the audio session.

	:param session: audio session
	:return: the volume interface of the session
	:raises COMError: the session is not available anymore
	"""
	return cast(SimpleVolume, session.QueryInterface(ISimpleAudioVolume))


def getSessionChannels(session: Session) -> ChannelVolume:
	"""Get the volume interface of the channels of the audio session.

	:param session: audio session
	:return: the volume interface of the channels of the session
	:raises COMError: the session is not available anymore
	"""
	return cast(ChannelVolume, session.QueryInterface(IChannelAudioVolume))
