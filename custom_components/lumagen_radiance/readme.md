# Lumagen Radiance Integration for Home Assistant

This integration allows you to control your Lumagen Radiance XE video processor via RS232-over-TCP.

## Features
- Power Control
- Input Selection (1-18)
- Audio Routing (per input)
- Aspect Ratio Selection
- Memory Management
- PIP Controls
- Menu Navigation

## Installation
1. Install via HACS (Custom Repository: `https://github.com/yourusername/lumagen_radiance`)
2. Restart Home Assistant
3. Add the integration via the UI

## Configuration
- **Host:** IP address of your RS232-to-TCP converter
- **Port:** Port number of your RS232-to-TCP converter (default: 10001)
- **Input Labels:** Configure labels for each input (1-18) in the integration options

## Commands
The integration uses commands from the Lumagen Radiance Tech Tip 11. Some commands (e.g., PIP Position/Source, Audio Set) may need to be verified with your full PDF.

## Notes
- The integration polls the device every 5 seconds for status updates.
- Ensure your RS232-to-TCP converter passes raw bytes transparently.
