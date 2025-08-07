<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# WebSocket Printer Client - Copilot Instructions

This is a Python WebSocket client project for thermal/label printer integration.

## Project Context

- **Purpose**: Connect to WebSocket server and handle print jobs via serial communication
- **Target Hardware**: Thermal printers (ESC/POS, ZPL compatible)
- **Communication**: WebSocket for server communication, Serial port for printer communication
- **Label Types**: Location labels, Pallet labels, Test labels

## Code Style Guidelines

- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Implement proper error handling with logging
- Use async/await for WebSocket operations
- Use dataclasses for configuration structures
- Implement proper resource cleanup (serial ports, connections)

## Key Components

1. **WebSocketPrinterClient**: Main client class for WebSocket communication
2. **SerialPrinterInterface**: Serial port communication handler
3. **Label Generators**: ESC/POS and ZPL command generators
4. **Configuration**: Environment-based configuration management

## Development Guidelines

- Always handle serial port exceptions gracefully
- Implement reconnection logic for WebSocket connections
- Log all important operations and errors
- Support multiple printer types and protocols
- Use factory patterns for label generators
- Validate configurations before use

## Testing Considerations

- Mock serial port connections for unit tests
- Test with different printer types and baud rates
- Validate label command generation
- Test WebSocket connection handling and reconnection
- Verify error handling scenarios

## Dependencies

- `python-socketio` for WebSocket communication
- `pyserial` for serial port communication
- Standard library modules for async operations and configuration
