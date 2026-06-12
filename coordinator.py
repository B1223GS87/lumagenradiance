"""Data update coordinator for Lumagen Radiance."""

import asyncio
import logging
import re
from typing import Optional, Dict, Any
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    QUERY_INPUT_INFO,
    QUERY_INPUT_VIDEO,
    QUERY_AUDIO_SELECT,
    QUERY_INPUT_ASPECT,
    QUERY_FULL_INFO,
    RESPONSE_PREFIX,
    RESPONSE_TERMINATOR,
)

_LOGGER = logging.getLogger(__name__)

class LumagenDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Class to manage fetching data from the Lumagen Radiance."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._connected = False
        self._lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=asyncio.timedelta(seconds=5),
        )

    async def async_connect(self) -> None:
        """Connect to the Radiance."""
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self._connected = True
            _LOGGER.info("Connected to Lumagen Radiance at %s:%d", self.host, self.port)
            self.hass.async_create_task(self._read_loop())
        except Exception as e:
            _LOGGER.error("Failed to connect: %s", e)
            self._connected = False
            raise HomeAssistantError(f"Connection failed: {e}")

    async def _read_loop(self) -> None:
        """Read data from the socket."""
        while self._connected:
            try:
                data = await self.reader.read(4096)
                if not data:
                    _LOGGER.warning("Connection lost")
                    self._connected = False
                    break
                self._handle_data(data)
            except Exception as e:
                _LOGGER.error("Read error: %s", e)
                self._connected = False

    def _handle_data(self, data: bytes) -> None:
        """Parse incoming data."""
        text = data.decode("utf-8", errors="ignore")
        # Split by response prefix and terminator
        chunks = re.split(r'(\r\n|\{)', text)
        for chunk in chunks:
            if not chunk or chunk in ('\r\n', '{'):
                continue
            match = re.search(r'!.*?(ZQI\d{2})', chunk)
            if match:
                query_code = match.group(1)
                data_str = chunk[chunk.find('!')+1:chunk.find(query_code)].strip().rstrip('<CR>')
                self._process_query(query_code, data_str)

    def _process_query(self, query_code: str, data: str) -> None:
        """Process query response."""
        if query_code == QUERY_INPUT_INFO:
            # Example: !I00,1,A,1 -> Logical Input 1, Memory A, Physical Input 1
            parts = data.split(',')
            if len(parts) >= 3:
                self.data['input_number'] = int(parts[0])
                self.data['input_memory'] = parts[1]
                self.data['physical_input'] = int(parts[2])
        elif query_code == QUERY_INPUT_VIDEO:
            # Example: !I01,1,5992,720,480,1,0 -> Active, Rate, Res, Interlaced, etc.
            parts = data.split(',')
            if len(parts) >= 6:
                self.data['video_active'] = int(parts[0]) == 1
                self.data['vertical_rate'] = int(parts[1])
                self.data['horizontal_res'] = int(parts[2])
                self.data['vertical_res'] = int(parts[3])
                self.data['interlaced'] = int(parts[4])
                self.data['frame_packed'] = int(parts[5])
        elif query_code == QUERY_AUDIO_SELECT:
            # Example: !I04,0 -> Audio Source 0 (HDMI 1)
            parts = data.split(',')
            if len(parts) >= 2:
                self.data['audio_source'] = int(parts[1])
        elif query_code == QUERY_INPUT_ASPECT:
            # Example: !I20,0 -> Aspect 0 (4:3)
            parts = data.split(',')
            if len(parts) >= 2:
                self.data['input_aspect'] = int(parts[1])
        elif query_code == QUERY_FULL_INFO:
            # Complex response, parse key fields
            parts = data.split(',')
            if len(parts) >= 16:
                self.data['input_status'] = int(parts[0])
                self.data['source_vertical_rate'] = int(parts[1])
                self.data['source_vertical_resolution'] = int(parts[2])
                self.data['three_d_mode'] = int(parts[3])
                self.data['input_config_number'] = int(parts[4])
                self.data['source_raster_aspect'] = int(parts[5])
                self.data['source_content_aspect'] = int(parts[6])
                self.data['nls_active'] = parts[7]
                self.data['three_d_output_mode'] = int(parts[8])
                self.data['output_on'] = int(parts[9], 16)
                self.data['output_cms_selected'] = int(parts[10])
                self.data['output_style_selected'] = int(parts[11])
                self.data['output_vertical_rate'] = int(parts[12])
                self.data['output_vertical_res'] = int(parts[13])
                self.data['output_aspect'] = int(parts[14])
                self.data['output_mode'] = parts[15]

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via queries."""
        if not self._connected or not self.writer:
            raise HomeAssistantError("Device not connected")

        queries = [
            QUERY_INPUT_INFO,
            QUERY_INPUT_VIDEO,
            QUERY_AUDIO_SELECT,
            QUERY_INPUT_ASPECT,
            QUERY_FULL_INFO,
        ]

        async with self._lock:
            for query in queries:
                try:
                    self.writer.write(query.encode("utf-8"))
                    await self.writer.drain()
                    # Wait for response (handled in _read_loop)
                    await asyncio.sleep(0.1)  # Small delay to ensure response is processed
                except Exception as e:
                    _LOGGER.error("Query failed: %s", e)
                    raise UpdateFailed(f"Query failed: {e}")

        return self.data

    async def send_command(self, command: str, requires_terminator: bool = False) -> None:
        """Send a command to the Radiance."""
        if not self._connected or not self.writer:
            raise HomeAssistantError("Device not connected")

        async with self._lock:
            if requires_terminator:
                self.writer.write(command.encode("utf-8") + b"\r")
            else:
                self.writer.write(command.encode("utf-8"))
            await self.writer.drain()
            _LOGGER.debug("Sent command: %s", command)

    async def async_close(self) -> None:
        """Close the connection."""
        self._connected = False
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
