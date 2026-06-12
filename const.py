"""Constants for the Lumagen Radiance integration."""

DOMAIN = "lumagen_radiance"

# Power Commands (from images)
COMMAND_POWER_ON = "%"
COMMAND_POWER_STANDBY = "$"

# Input Selection (from images)
# Format: 'i' + number (e.g., 'i2' for input 2, 'i+2' for input 12)
COMMAND_INPUT = "i"

# Aspect Ratio Commands (from images)
COMMAND_ASPECT_43 = "n"
COMMAND_ASPECT_169 = "*"
COMMAND_ASPECT_43_NLS = "["
COMMAND_ASPECT_169_NLS = "*N"  # Multi-char command
COMMAND_ASPECT_43_LBOX_NLS = "]N"  # Multi-char command

# Memory Commands (from images)
COMMAND_MEMORY_A = "a"
COMMAND_MEMORY_B = "b"
COMMAND_MEMORY_C = "c"
COMMAND_MEMORY_D = "d"
COMMAND_SAVE = "S"

# PIP Commands (from images)
COMMAND_PIP_OFF = "e"
COMMAND_PIP_SEL = "p"
COMMAND_PIP_SWAP = "r"
COMMAND_PIP_MODE = "m"
# Note: PIP Position/Source commands not in images, placeholders added
COMMAND_PIP_SOURCE = "P{source}"  # Verify exact command in full PDF
COMMAND_PIP_POSITION = "M{x},{y}"  # Verify exact command in full PDF

# Menu Navigation Commands (from images)
COMMAND_MENU = "M"
COMMAND_MENU_EXIT = "X"
COMMAND_MENU_HELP = "U"
COMMAND_MENU_CLR = "!"
COMMAND_MENU_OK = "k"
COMMAND_MENU_UP = "^"
COMMAND_MENU_DOWN = "v"
COMMAND_MENU_LEFT = "<"
COMMAND_MENU_RIGHT = ">"

# Audio Routing (from images)
# Note: ZQI04 returns current audio. Set command not in images, placeholder added
COMMAND_AUDIO_SELECT = "A{audio_code}"  # Verify exact command in full PDF

# Query Commands (from images)
QUERY_INPUT_INFO = "ZQI00"  # Returns logical input, memory, physical input
QUERY_INPUT_VIDEO = "ZQI01"  # Returns video status, resolution, etc.
QUERY_INPUT_PATTERN = "ZQI02"  # Returns pattern info
QUERY_AUDIO_SELECT = "ZQI04"  # Returns current audio source (0-5 HDMI, 6-11 coax, etc.)
QUERY_INPUT_ASPECT = "ZQI20"  # Returns current input aspect (0-9)
QUERY_FULL_INFO = "ZQI21"  # Full system info

# Query Response Parsing
RESPONSE_PREFIX = "!"
RESPONSE_TERMINATOR = "<CR><LF>"

# Input Labels (Config)
INPUT_LABELS = {
    1: "Apple TV 4K",
    2: "PS5",
    3: "LaserDisc",
    4: "Blu-ray",
    5: "PC",
    6: "Cable Box",
    7: "Network Player",
    8: "Game Console 2",
    9: "VCR",
    10: "PC Alt",
    11: "Unused 1",
    12: "Unused 2",
    13: "Unused 3",
    14: "Unused 4",
    15: "Unused 5",
    16: "Unused 6",
    17: "Unused 7",
    18: "Unused 8",
}

# Audio Source Mapping (Config)
AUDIO_SOURCES = {
    0: "HDMI 1", 1: "HDMI 2", 2: "HDMI 3", 3: "HDMI 4", 4: "HDMI 5", 5: "HDMI 6",
    6: "Coax 1", 7: "Coax 2", 8: "Coax 3", 9: "Coax 4", 10: "Coax 5", 11: "Coax 6",
    12: "Optical 1", 13: "Optical 2", 14: "Stereo 1", 15: "Stereo 2", 16: "Stereo 3", 17: "Stereo 4"
}
