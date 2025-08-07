# WebSocket Printer Client

Python client application that connects to the WebSocket server and handles print jobs by sending commands to thermal printers via serial port.

## 🔧 Features

- **WebSocket Communication**: Real-time connection to the Node.js print server
- **Serial Port Support**: Direct communication with thermal printers
- **Multiple Label Formats**: Support for location, pallet, and test labels
- **Multiple Printer Types**: ESC/POS and ZPL command generation
- **Auto-Reconnection**: Automatic reconnection to server on connection loss
- **Error Handling**: Comprehensive error handling and logging
- **Configuration Management**: Environment-based configuration

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- Serial port access (USB, RS232, etc.)
- Thermal printer (ESC/POS or ZPL compatible)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Setup

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` file with your configuration:
```bash
# Printer Configuration
PRINTER_ID=PRINTER_001
PRINTER_NAME=Main Printer
PRINTER_TYPE=thermal
PRINTER_LOCATION=Warehouse A

# Serial Port Configuration (adjust for your system)
SERIAL_PORT=/dev/ttyUSB0  # Linux/Mac
# SERIAL_PORT=COM1         # Windows
BAUD_RATE=9600
SERIAL_TIMEOUT=1.0

# Server Configuration
SERVER_URL=http://localhost:25625
```

## 🚀 Usage

### Quick Start

Run the interactive client:
```bash
python run_client.py
```

The script will:
1. List available serial ports
2. Ask for printer configuration
3. Connect to the WebSocket server
4. Start processing print jobs

### Advanced Usage

For automated deployment, use environment variables:

```bash
# Set environment variables
export PRINTER_ID=PRINTER_WAREHOUSE_A
export PRINTER_NAME="Warehouse A Main Printer"
export SERIAL_PORT=/dev/ttyUSB0
export SERVER_URL=http://192.168.1.100:25625

# Run the client
python printer_client.py
```

### Configuration Options

#### Printer Types
- `thermal` - ESC/POS thermal printers (default)
- `zebra` - Zebra ZPL printers
- `label` - Generic label printers

#### Serial Port Examples
- **Linux**: `/dev/ttyUSB0`, `/dev/ttyACM0`
- **macOS**: `/dev/cu.usbserial-*`, `/dev/tty.usbserial-*`
- **Windows**: `COM1`, `COM2`, etc.

#### Baud Rates
Common baud rates for thermal printers:
- `9600` (most common)
- `19200`
- `38400`
- `115200`

## 🖨️ Supported Printers

### ESC/POS Compatible Printers
- Epson TM series (TM-T20, TM-T88, etc.)
- Star Micronics TSP series
- Citizen CT-S series
- Generic thermal receipt printers

### ZPL Compatible Printers
- Zebra ZD410, ZD420
- Zebra GK420d, GK420t
- Zebra ZT series

## 📋 Label Formats

### Location Labels
```
LOCATION LABEL
================================
*LOC000001*
Location: A-01-01
Warehouse: WH001
Type: SHELF
Position: A-01-01-01
Max Weight: 1000 kg
Max Volume: 500 m³
--------------------------------
Created: 2025-08-07 10:30:00
Printed: 2025-08-07 10:35:00
```

### Pallet Labels
```
PALLET LABEL
================================
*PAL000001*
Pallet ID: 1
Type: EURO
Status: AVAILABLE
Warehouse: WH001
Weight: 500/1000 kg
Volume: 250/500 m³
--------------------------------
Created: 2025-08-07 10:30:00
Printed: 2025-08-07 10:35:00
```

### Test Labels
```
TEST LABEL
====================
Printer Test
Time: 10:35:00
====================
Print Test Successful
```

## 🔧 Troubleshooting

### Common Issues

#### Serial Port Access Denied
**Linux/macOS:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again
```

#### Port Not Found
```bash
# List available ports
python -c "import serial.tools.list_ports; [print(p.device, p.description) for p in serial.tools.list_ports.comports()]"
```

#### Connection Issues
1. Check if the WebSocket server is running
2. Verify the server URL in configuration
3. Check network connectivity
4. Look at the logs for detailed error messages

#### Printer Not Responding
1. Check serial port and baud rate settings
2. Verify printer is powered on and connected
3. Test with printer's self-test function
4. Try different baud rates (9600, 19200, 38400)

### Logging

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python printer_client.py
```

Log to file:
```bash
export LOG_FILE=printer_client.log
python printer_client.py
```

## 🧪 Testing

### Test Printer Connection
```python
python -c "
from config import PrinterConfig, PrinterType
from printer_client import SerialPrinterInterface

config = PrinterConfig(
    printer_id='TEST',
    printer_name='Test Printer',
    printer_type=PrinterType.THERMAL,
    location='Test',
    serial_port='/dev/ttyUSB0'  # adjust for your system
)

printer = SerialPrinterInterface(config.serial_port, config.baud_rate)
if printer.connect():
    print('Printer connected successfully!')
    printer.send_command('Test message\n')
    printer.disconnect()
else:
    print('Failed to connect to printer')
"
```

### Test WebSocket Connection
```python
python -c "
import asyncio
import socketio

async def test_connection():
    sio = socketio.AsyncClient()
    try:
        await sio.connect('http://localhost:25625')
        print('WebSocket connection successful!')
        await sio.disconnect()
    except Exception as e:
        print(f'Connection failed: {e}')

asyncio.run(test_connection())
"
```

## 📚 API Reference

### WebSocketPrinterClient Class

Main client class that handles WebSocket communication and print job processing.

#### Methods

- `connect_to_server()` - Connect to WebSocket server
- `connect_to_printer()` - Connect to serial printer
- `register_printer()` - Register printer with server
- `process_print_job(job)` - Process a print job
- `start()` - Start the client main loop

### SerialPrinterInterface Class

Handles serial communication with printers.

#### Methods

- `connect()` - Connect to serial port
- `disconnect()` - Disconnect from serial port
- `send_command(command)` - Send text command
- `send_raw_bytes(data)` - Send raw bytes

### Label Generators

- `ESCPOSLabelGenerator` - For thermal printers
- `ZPLLabelGenerator` - For Zebra printers

## 🔄 Integration

This client integrates with the main WebSocket server. Make sure the server is running:

```bash
# In the main project directory
cd /Users/onderalpselcuk/works/bpBack
npm start
```

The server should be accessible at `http://localhost:25625` with WebSocket support.

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for detailed error messages
3. Create an issue with detailed information about your setup
