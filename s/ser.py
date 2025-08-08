import json
import time
import usb.core
import usb.util

def send_zpl_to_printer_via_usb(zpl_command):
    # Find the Zebra printer by its Vendor ID and Product ID
    dev = usb.core.find(idVendor=0x0A5F, idProduct=0x0164)  # Zebra printer Vendor & Product ID

    if dev is None:
        raise ValueError("Zebra printer not found")

    # On Windows, we don't need to detach the kernel driver
    try:
        # Set the active configuration (interface)
        dev.set_configuration()

        # Get the OUT endpoint (0x01)
        endpoint_out = None
        for cfg in dev:
            for intf in cfg:
                for ep in intf:
                    if ep.bEndpointAddress == 0x01:  # OUT endpoint
                        endpoint_out = ep
                        break
                if endpoint_out:
                    break
            if endpoint_out:
                break

        if endpoint_out is None:
            raise ValueError("OUT endpoint (0x01) not found")

        # Send data to the OUT endpoint (Bulk OUT)
        dev.write(endpoint_out.bEndpointAddress, zpl_command.encode('utf-8'), timeout=1000)
        print("ZPL command sent successfully.")
    except usb.core.USBError as e:
        print(f"Error sending ZPL command: {e}")

    # Release the interface after sending the command
    usb.util.release_interface(dev, 0)
    print("Interface released.")

    # Add a small delay before the next print
    time.sleep(1)  # Adjust the delay if necessary

    
for i in range(1, 50):
    zpl_label = f''' ^XA
        ^FX set width and height
        ^PW799 ^FX size in points = 100 mm width
        ^LL630   ^FX size in points = 80 mm height
        ^CI28
        ^MMT    ^FX set media type to Tear-off
        ^BY3,3  ^FX set the bar code height and gap between labels (gap in dots, 3 mm = 12 dots at 8 dots/mm)
        ^FX border start
        ^FO10,10^GB750,2,2^FS ^FX TOP
        ^FO10,10^GB2,600,2,B^FS ^FX LEFT
        ^FO759,10^GB2,600,2,B^FS ^FX RIGHT
        ^FO10,618^GB750,2,2^FS ^FX BOTTOM
        ^FX border end
        ^FX companySection
        ^FO18,25
        ^A0N,25,25
        ^FDFrima Adi / Depo^FS

        ^FO25,55
        ^A0N,50,50
        ^FDBil Plastik Ambalaj / Ana Fabrika^FS

        ^FO10,110^GB750,2,2^FS 
        ^FX end of CompanySection

        ^FO18,120
        ^A0N,35,35
        ^FDSevkiyat Ürün Deposu  ^FS  ^FS ^FX 30 charecter max

        ^FO18,160
        ^A0N,35,35
        ^FO10,160^GB750,2,2^FS 

        ^FO18,170
        ^A0N,42,42
        ^FD^FS ^FX 35 charecter max
        ^FO18,220
        ^A0N,42,42
        ^FD^FS ^FX 35 charecter max
        ^FO10,270^GB750,2,2^FS 
        ^FO10,275^GB750,2,2^FS 

        
        
        ^FX start bottom table
        ^CF0,40
        ^FO10,300^FB375,1,0,C^FDAlt Raf - DP-S-{i}1^FS
        ^FO90,370
        ^BQN,2,10
        ^FDLA,DP-S-{i}1^FS
        ^FO10,280^GB375,340,2^FS
        ^FO385,280^GB375,340,2^FS

        ^CF0,40
        ^FO390,300^FB375,1,0,C^FDÜst Raf - DP-S-{i}2^FS
        ^FO470,370
        ^BQN,2,10
        ^FDLA,DP-S-{i}2^FS
        ^FO10,280^GB375,340,2^FS
        ^FO385,280^GB375,340,2^FS
        ^XZ'''
    print(zpl_label)
    send_zpl_to_printer_via_usb(zpl_label)
