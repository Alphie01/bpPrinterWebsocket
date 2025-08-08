import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for port in ports:
    if "Zebra" in port.description:
        print(f"Zebra yazıcısı bağlı: {port.device}")