"""TCP utilities for receiving MYO Armband messages.

This module provides a hardware-independent TCP JSON-lines receiver that can be
used to collect messages from a separate MYO sender process.

The receiver is intentionally independent from the MYO SDK. It only handles:

- TCP server creation.
- JSON-lines message reception.
- Thread-safe buffering.
- START/STOP command exchange.
- Basic timestamp annotation.

The actual MYO hardware acquisition should remain in a separate sender process.
"""

from __future__ import annotations

import json
import socket
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional


@dataclass(frozen=True)
class MyoReceiverConfig:
    """Configuration for the MYO TCP receiver."""

    host: str = "0.0.0.0"
    port: int = 9999
    accept_timeout_s: float = 1.0
    recv_timeout_s: float = 1.0
    buffer_size: int = 4096
    encoding: str = "utf-8"


class MyoTCPReceiver:
    """TCP JSON-lines receiver for MYO messages."""

    def __init__(
        self,
        config: Optional[MyoReceiverConfig] = None,
        start_event: Optional[threading.Event] = None,
    ) -> None:
        self.config = config or MyoReceiverConfig()
        self.start_event = start_event

        self._messages: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._server_thread: Optional[threading.Thread] = None
        self._server_socket: Optional[socket.socket] = None
        self._connection: Optional[socket.socket] = None
        self._recv_buffer = ""
        self._running = False
        self._start_time_s: Optional[float] = None

    @property
    def is_running(self) -> bool:
        """Return whether the receiver server loop is active."""
        return self._running

    @property
    def start_time_s(self) -> Optional[float]:
        """Return the receiver start time in epoch seconds."""
        return self._start_time_s

    def start(self) -> None:
        """Start the TCP server in a background thread."""
        if self._running:
            return

        self._running = True
        self._server_thread = threading.Thread(target=self._run_server, daemon=True)
        self._server_thread.start()

    def stop(self, join_timeout_s: float = 2.0) -> None:
        """Stop the receiver and close sockets."""
        self._running = False

        try:
            if self._connection is not None:
                self._connection.close()
        except OSError:
            pass

        try:
            if self._server_socket is not None:
                self._server_socket.close()
        except OSError:
            pass

        if self._server_thread is not None:
            self._server_thread.join(timeout=join_timeout_s)

    def clear(self) -> None:
        """Clear all buffered messages and partial text buffer."""
        with self._lock:
            self._messages.clear()
        self._recv_buffer = ""

    def get_messages(self) -> List[Dict[str, Any]]:
        """Return a copy of buffered messages."""
        with self._lock:
            return list(self._messages)

    def send_command(self, command: str) -> bool:
        """Send a command to the connected MYO sender.

        Parameters
        ----------
        command:
            Command string, for example ``START`` or ``STOP``.

        Returns
        -------
        bool
            True if the command was sent, False otherwise.
        """
        if self._connection is None:
            return False

        payload = json.dumps({"cmd": command}) + "\n"

        try:
            self._connection.sendall(payload.encode(self.config.encoding))
            return True
        except OSError:
            return False

    def send_start(self) -> bool:
        """Send START command to the connected MYO sender."""
        return self.send_command("START")

    def send_stop(self) -> bool:
        """Send STOP command to the connected MYO sender."""
        return self.send_command("STOP")

    def _run_server(self) -> None:
        """Run the TCP server loop."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket = server_socket

        try:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.config.host, self.config.port))
            server_socket.listen(1)
            server_socket.settimeout(self.config.accept_timeout_s)

            if self.start_event is not None:
                self.start_event.wait()

            self._start_time_s = time.time()

            while self._running and self._connection is None:
                try:
                    connection, _address = server_socket.accept()
                    self._connection = connection
                    connection.settimeout(self.config.recv_timeout_s)
                    self.send_start()
                except socket.timeout:
                    continue

            if self._connection is not None:
                self._receive_loop(self._connection)

        finally:
            self._safe_close_socket(self._connection)
            self._safe_close_socket(server_socket)
            self._connection = None
            self._server_socket = None
            self._running = False

    def _receive_loop(self, connection: socket.socket) -> None:
        """Receive and parse JSON-lines messages."""
        while self._running:
            try:
                data = connection.recv(self.config.buffer_size)
            except socket.timeout:
                continue
            except OSError:
                break

            if not data:
                break

            self._recv_buffer += data.decode(self.config.encoding)

            while "\n" in self._recv_buffer:
                line, self._recv_buffer = self._recv_buffer.split("\n", 1)
                line = line.strip()

                if not line:
                    continue

                message = self._parse_message(line)

                if message is None:
                    continue

                self._append_message(message)

                if message.get("marker") == 99.0:
                    self.send_stop()
                    self._running = False
                    break

    def _parse_message(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse and annotate a single JSON message."""
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            return None

        if not isinstance(message, dict):
            return None

        now = time.time()
        annotated = dict(message)
        annotated["timestamp_received_s"] = now

        if self._start_time_s is not None:
            annotated["timestamp_rel"] = now - self._start_time_s

        return annotated

    def _append_message(self, message: Mapping[str, Any]) -> None:
        """Append a message to the thread-safe buffer."""
        with self._lock:
            self._messages.append(dict(message))

    @staticmethod
    def _safe_close_socket(sock: Optional[socket.socket]) -> None:
        """Close a socket safely."""
        if sock is None:
            return

        try:
            sock.close()
        except OSError:
            pass
