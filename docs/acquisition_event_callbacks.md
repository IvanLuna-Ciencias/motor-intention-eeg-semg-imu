# Acquisition event callbacks

This document describes the event callback layer used by the acquisition protocol runner.

## Module

~~~text
src/motor_intention/acquisition/event_callbacks.py
~~~

## Purpose

The callback layer allows protocol events to be connected to different actions without hardcoding hardware logic inside the protocol runner.

For example, when the protocol emits an event, callbacks can:

- Record the event in memory.
- Save the event later as CSV.
- Insert markers into MindRove.
- Forward markers to other devices in future versions.

## Available callbacks

### ProtocolEventRecorder

Records emitted protocol events.

Useful for:

- Events preview.
- Tests.
- Offline validation.
- Later saving with `save_events_csv`.

### DeviceMarkerCallback

Forwards protocol markers to a device method.

Expected device method:

~~~text
insert_marker(marker)
~~~

This matches the MindRove wrapper method:

~~~text
MindRoveEEGDevice.insert_marker(marker)
~~~

## Design note

The protocol runner does not know whether a callback records events, inserts EEG markers, or forwards commands.

This keeps the protocol logic hardware-independent and easier to test.

## Future use

The next planned integration is to connect:

~~~text
ProtocolRunner + DeviceMarkerCallback + MindRoveEEGDevice
~~~

so that the full trial protocol can insert EEG markers during real acquisition.
