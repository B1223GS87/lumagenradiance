 """Entities for the Lumagen Radiance integration."""

import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.button import ButtonEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    COMMAND_POWER_ON,
    COMMAND_POWER_STANDBY,
    COMMAND_INPUT,
    COMMAND_ASPECT_43,
    COMMAND_ASPECT_169,
    COMMAND_ASPECT_43_NLS,
    COMMAND_ASPECT_169_NLS,
    COMMAND_MEMORY_A,
    COMMAND_MEMORY_B,
    COMMAND_MEMORY_C,
    COMMAND_MEMORY_D,
    COMMAND_SAVE,
    COMMAND_PIP_OFF,
    COMMAND_PIP_SEL,
    COMMAND_PIP_SWAP,
    COMMAND_PIP_MODE,
    COMMAND_MENU,
    COMMAND_MENU_EXIT,
    COMMAND_MENU_HELP,
    COMMAND_MENU_CLR,
    COMMAND_MENU_OK,
    COMMAND_MENU_UP,
    COMMAND_MENU_DOWN,
    COMMAND_MENU_LEFT,
    COMMAND_MENU_RIGHT,
    INPUT_LABELS,
    AUDIO_SOURCES,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lumagen Radiance entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    # Power Switch
    entities.append(LumagenPowerSwitch(coordinator))

    # Input Select
    entities.append(LumagenInputSelect(coordinator))

    # Audio Select (per input)
    for input_num in range(1, 19):
        entities.append(LumagenAudioSelect(coordinator, input_num))

    # Aspect Ratio Select
    entities.append(LumagenAspectSelect(coordinator))

    # Memory Select
    entities.append(LumagenMemorySelect(coordinator))

    # PIP Controls
    entities.append(LumagenPIPControl(coordinator))

    # Menu Navigation Buttons
    entities.append(LumagenMenuButton(coordinator, "Menu", COMMAND_MENU, False))
    entities.append(LumagenMenuButton(coordinator, "Exit", COMMAND_MENU_EXIT, False))
    entities.append(LumagenMenuButton(coordinator, "Help", COMMAND_MENU_HELP, False))
    entities.append(LumagenMenuButton(coordinator, "Clear", COMMAND_MENU_CLR, False))
    entities.append(LumagenMenuButton(coordinator, "OK", COMMAND_MENU_OK, False))
    entities.append(LumagenMenuButton(coordinator, "Up", COMMAND_MENU_UP, False))
    entities.append(LumagenMenuButton(coordinator, "Down", COMMAND_MENU_DOWN, False))
    entities.append(LumagenMenuButton(coordinator, "Left", COMMAND_MENU_LEFT, False))
    entities.append(LumagenMenuButton(coordinator, "Right", COMMAND_MENU_RIGHT, False))

    # Sensors
    entities.append(LumagenInputSensor(coordinator))
    entities.append(LumagenAudioSensor(coordinator))
    entities.append(LumagenAspectSensor(coordinator))

    async_add_entities(entities)

class LumagenPowerSwitch(SwitchEntity):
    """Representation of a Lumagen Radiance power switch."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._attr_name = "Lumagen Radiance Power"
        self._attr_unique_id = "lumagen_power"

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if device is on."""
        # Check if video is active (ZQI01 returns 1 if active)
        return self._coordinator.data.get('video_active', False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the device."""
        await self._coordinator.send_command(COMMAND_POWER_ON, requires_terminator=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the device."""
        await self._coordinator.send_command(COMMAND_POWER_STANDBY, requires_terminator=True)

class LumagenInputSelect(SelectEntity):
    """Representation of a Lumagen Radiance input selector."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._attr_name = "Lumagen Radiance Input"
        self._attr_unique_id = "lumagen_input"
        self._options = [f"Input {i}" for i in range(1, 19)]

    @property
    def current_option(self) -> Optional[str]:
        """Return the current input."""
        input_num = self._coordinator.data.get('input_number')
        if input_num:
            return f"Input {input_num}"
        return None

    async def async_select_option(self, option: str) -> None:
        """Select an input."""
        input_num = int(option.split(" ")[1])
        if input_num < 10:
            command = f"{COMMAND_INPUT}{input_num}"
        else:
            command = f"{COMMAND_INPUT}+{input_num - 10}"
        await self._coordinator.send_command(command, requires_terminator=False)

class LumagenAudioSelect(SelectEntity):
    """Representation of a Lumagen Radiance audio selector."""

    def __init__(self, coordinator: DataUpdateCoordinator, input_num: int) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._input_num = input_num
        self._attr_name = f"Lumagen Radiance Audio Input {input_num}"
        self._attr_unique_id = f"lumagen_audio_{input_num}"
        self._options = list(AUDIO_SOURCES.values())

    @property
    def current_option(self) -> Optional[str]:
        """Return the current audio source."""
        audio_source = self._coordinator.data.get('audio_source')
        if audio_source is not None and audio_source in AUDIO_SOURCES:
            return AUDIO_SOURCES[audio_source]
        return None

    async def async_select_option(self, option: str) -> None:
        """Select an audio source."""
        # Find the code for the option
        for code, name in AUDIO_SOURCES.items():
            if name == option:
                # Placeholder command, verify with full PDF
                command = COMMAND_AUDIO_SELECT.replace("{audio_code}", str(code))
                await self._coordinator.send_command(command, requires_terminator=True)
                break

class LumagenAspectSelect(SelectEntity):
    """Representation of a Lumagen Radiance aspect ratio selector."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._attr_name = "Lumagen Radiance Aspect Ratio"
        self._attr_unique_id = "lumagen_aspect"
        self._options = [
            "4:3", "16:9", "4:3 NLS", "16:9 NLS", "4:3 LBOX NLS"
        ]

    @property
    def current_option(self) -> Optional[str]:
        """Return the current aspect ratio."""
        aspect = self._coordinator.data.get('input_aspect')
        aspect_map = {
            0: "4:3", 1: "16:9", 2: "4:3 NLS", 3: "16:9 NLS", 4: "4:3 LBOX NLS"
        }
        return aspect_map.get(aspect)

    async def async_select_option(self, option: str) -> None:
        """Select an aspect ratio."""
        command_map = {
            "4:3": COMMAND_ASPECT_43,
            "16:9": COMMAND_ASPECT_169,
            "4:3 NLS": COMMAND_ASPECT_43_NLS,
            "16:9 NLS": COMMAND_ASPECT_169_NLS,
            "4:3 LBOX NLS": COMMAND_ASPECT_43_LBOX_NLS,
        }
        command = command_map.get(option)
        if command:
            await self._coordinator.send_command(command, requires_terminator=False)

class LumagenMemorySelect(SelectEntity):
    """Representation of a Lumagen Radiance memory selector."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._attr_name = "Lumagen Radiance Memory"
        self._attr_unique_id = "lumagen_memory"
        self._options = ["MEMA", "MEMB", "MEMC", "MEMD"]

    @property
    def current_option(self) -> Optional[str]:
        """Return the current memory."""
        memory = self._coordinator.data.get('input_memory')
        if memory:
            return f"MEM{memory.upper()}"
        return None

    async def async_select_option(self, option: str) -> None:
        """Select a memory."""
        memory_code = option[3].lower()  # 'A', 'B', 'C', 'D'
        command_map = {
            "a": COMMAND_MEMORY_A,
            "b": COMMAND_MEMORY_B,
            "c": COMMAND_MEMORY_C,
            "d": COMMAND_MEMORY_D,
        }
        command = command_map.get(memory_code)
        if command:
            await self._coordinator.send_command(command, requires_terminator=False)

    async def async_save(self) -> None:
        """Save the current memory."""
        await self._coordinator.send_command(COMMAND_SAVE, requires_terminator=True)

class LumagenPIPControl(ButtonEntity):
    """Representation of a Lumagen Radiance PIP control."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._attr_name = "Lumagen Radiance PIP"
        self._attr_unique_id = "lumagen_pip"

    async def async_press(self) -> None:
        """Press the PIP button."""
        # Placeholder: Cycle through PIP modes
        await self._coordinator.send_command(COMMAND_PIP_MODE, requires_terminator=False)

class LumagenMenuButton(ButtonEntity):
    """Representation of a Lumagen Radiance menu button."""

    def __init__(self, coordinator: DataUpdateCoordinator, name: str, command: str, requires_terminator: bool) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._name = name
        self._command = command
        self._requires_terminator = requires_terminator
        self._attr_name = f"Lumagen Radiance Menu {name}"
        self._attr_unique_id = f"lumagen_menu_{name.lower()}"

    async def async_press(self) -> None:
        """Press the menu button."""
        await self._coordinator.send_command(self._command, requires_terminator=self._requires_terminator)

class LumagenInputSensor(SensorEntity):
    """Representation of a Lumagen Radiance input sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._attr_name = "Lumagen Radiance Input Number"
        self._attr_unique_id = "lumagen_input_number"

    @property
    def native_value(self) -> Optional[int]:
        """Return the current input number."""
        return self._coordinator.data.get('input_number')

class LumagenAudioSensor(SensorEntity):
    """Representation of a Lumagen Radiance audio sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._attr_name = "Lumagen Radiance Audio Source"
        self._attr_unique_id = "lumagen_audio_source"

    @property
    def native_value(self) -> Optional[str]:
        """Return the current audio source."""
        audio_source = self._coordinator.data.get('audio_source')
        if audio_source is not None and audio_source in AUDIO_SOURCES:
            return AUDIO_SOURCES[audio_source]
        return None

class LumagenAspectSensor(SensorEntity):
    """Representation of a Lumagen Radiance aspect sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._attr_name = "Lumagen Radiance Aspect Ratio"
        self._attr_unique_id = "lumagen_aspect"

    @property
    def native_value(self) -> Optional[str]:
        """Return the current aspect ratio."""
        aspect = self._coordinator.data.get('input_aspect')
        aspect_map = {
            0: "4:3", 1: "16:9", 2: "4:3 NLS", 3: "16:9 NLS", 4: "4:3 LBOX NLS"
        }
        return aspect_map.get(aspect)
