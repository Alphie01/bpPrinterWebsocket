# COM Port Diagnostic Tools

This directory includes diagnostic tools to help resolve COM port connection issues with the WebSocket Printer Client.

## Quick Fix Tool

For immediate COM3 issues (most common):

```bash
python fix_com3.py
```

This tool will:
- Check if COM3 exists and is accessible
- Attempt automatic port recovery
- Find alternative working ports
- Provide step-by-step manual solutions
- Create a Windows batch file for advanced fixes

## Comprehensive Diagnostics

For detailed port analysis:

```bash
python port_diagnostics.py
```

Available options:
- `--scan`: Comprehensive scan of all COM ports
- `--find-printers`: Find ports likely connected to printers
- `--port COM3`: Test a specific port
- `--release COM3`: Attempt to force release a stuck port
- `--aggressive`: Use aggressive release methods (may terminate processes)

## Common Issues and Solutions

### Issue: "Permission denied - Port in use"

**Cause**: Another application is using the COM port (Arduino IDE, PuTTY, printer drivers, etc.)

**Solutions**:
1. Close all applications that might use COM ports
2. Run `python fix_com3.py` for automated fixes
3. Use Device Manager to disable/enable the port
4. Try USB direct connection instead

### Issue: "Cannot configure port"

**Cause**: Port driver issues or hardware conflicts

**Solutions**:
1. Update USB/printer drivers
2. Try different USB port
3. Restart Windows services (Print Spooler, Plug and Play)
4. Restart computer

### Issue: "Port does not exist"

**Cause**: Printer not properly connected or recognized

**Solutions**:
1. Check USB cable connection
2. Install printer drivers
3. Check Device Manager for unrecognized devices
4. Try different USB cable

## Alternative Connection Methods

If COM port issues persist, consider:

### USB Direct Connection
```bash
set CONNECTION_TYPE=usb
set USB_VENDOR_ID=0x0A5F
set USB_PRODUCT_ID=0x0164
```

### Network Connection (if supported)
Some printers support network printing via TCP/IP.

## Environment Variables

Set these to override auto-detection:

- `SERIAL_PORT=COM3` - Force specific COM port
- `CONNECTION_TYPE=serial|usb|auto` - Connection method
- `BAUD_RATE=9600` - Serial communication speed
- `USB_VENDOR_ID=0x0A5F` - USB vendor ID
- `USB_PRODUCT_ID=0x0164` - USB product ID

## Getting Help

1. Run `python fix_com3.py` first for common issues
2. Use `python port_diagnostics.py --scan` for detailed analysis
3. Check Windows Device Manager for hardware issues
4. Consult your printer manual for specific connection requirements

## Supported Printers

These tools work with various thermal and label printers:
- Zebra ZD220, ZD410, ZD420, GK420t, GC420t
- Brother QL series
- Epson TM-T series
- Dymo LabelWriter series
- Most ESC/POS compatible thermal printers
