"""
Label generation module for different printer types and formats
"""

import time
from typing import Dict, Any
from abc import ABC, abstractmethod


class LabelGeneratorBase(ABC):
    """Base class for label generators"""
    
    @abstractmethod
    def generate_location_label(self, data: Dict[str, Any]) -> str:
        """Generate location label"""
        pass
    
    @abstractmethod
    def generate_pallet_label(self, data: Dict[str, Any]) -> str:
        """Generate pallet label"""
        pass
    
    @abstractmethod
    def generate_test_label(self, data: Dict[str, Any]) -> str:
        """Generate test label"""
        pass


class ESCPOSLabelGenerator(LabelGeneratorBase):
    """ESC/POS command generator for thermal printers"""
    
    # ESC/POS Commands
    ESC = "\x1B"
    GS = "\x1D"
    
    # Control commands
    INIT = f"{ESC}@"  # Initialize printer
    CUT = f"{GS}V\x42\x00"  # Partial cut
    
    # Text formatting
    NORMAL_FONT = f"{ESC}!\x00"
    LARGE_FONT = f"{ESC}!\x30"
    BOLD_ON = f"{ESC}E\x01"
    BOLD_OFF = f"{ESC}E\x00"
    
    # Alignment
    ALIGN_LEFT = f"{ESC}a\x00"
    ALIGN_CENTER = f"{ESC}a\x01"
    ALIGN_RIGHT = f"{ESC}a\x02"
    
    def generate_location_label(self, data: Dict[str, Any]) -> str:
        """Generate ESC/POS commands for location label"""
        commands = []
        
        # Initialize printer
        commands.append(self.INIT)
        
        # Header
        commands.append(self.ALIGN_CENTER)
        commands.append(self.BOLD_ON)
        commands.append("LOCATION LABEL\n")
        commands.append(self.BOLD_OFF)
        commands.append("=" * 32 + "\n")
        
        # Barcode
        barcode = data.get('barcode', '')
        if barcode:
            commands.append(f"*{barcode}*\n")
        
        # Location data
        commands.append(self.ALIGN_LEFT)
        commands.append(self.NORMAL_FONT)
        
        commands.append(f"Location: {data.get('locationName', 'N/A')}\n")
        commands.append(f"Warehouse: {data.get('warehouseCode', 'N/A')}\n")
        commands.append(f"Type: {data.get('locationType', 'N/A')}\n")
        
        # Position info
        aisle = data.get('aisle', '')
        bay = data.get('bay', '')
        level = data.get('level', '')
        position = data.get('position', '')
        
        if aisle or bay or level or position:
            pos_str = f"{aisle}-{bay}-{level}"
            if position:
                pos_str += f"-{position}"
            commands.append(f"Position: {pos_str}\n")
        
        # Capacity info
        max_weight = data.get('maxWeight')
        if max_weight:
            commands.append(f"Max Weight: {max_weight} kg\n")
        
        max_volume = data.get('maxVolume')
        if max_volume:
            commands.append(f"Max Volume: {max_volume} m³\n")
        
        # Footer
        commands.append("-" * 32 + "\n")
        commands.append(f"Created: {data.get('createdAt', '')[:19]}\n")
        commands.append(f"Printed: {data.get('printedAt', time.strftime('%Y-%m-%d %H:%M:%S'))}\n")
        
        # Cut paper
        commands.append("\n")
        commands.append(self.CUT)
        
        return "".join(commands)
    
    def generate_pallet_label(self, data: Dict[str, Any]) -> str:
        """Generate ESC/POS commands for pallet label"""
        commands = []
        
        # Initialize printer
        commands.append(self.INIT)
        
        # Header
        commands.append(self.ALIGN_CENTER)
        commands.append(self.BOLD_ON)
        commands.append("PALLET LABEL\n")
        commands.append(self.BOLD_OFF)
        commands.append("=" * 32 + "\n")
        
        # Barcode
        barcode = data.get('barcode', '')
        if barcode:
            commands.append(f"*{barcode}*\n")
        
        # Pallet data
        commands.append(self.ALIGN_LEFT)
        commands.append(self.NORMAL_FONT)
        
        commands.append(f"Pallet ID: {data.get('id', 'N/A')}\n")
        commands.append(f"Type: {data.get('palletType', 'N/A')}\n")
        commands.append(f"Status: {data.get('status', 'N/A')}\n")
        commands.append(f"Warehouse: {data.get('warehouseCode', 'N/A')}\n")
        
        # Weight info
        current_weight = data.get('currentWeight', 0)
        max_weight = data.get('maxWeight', 0)
        commands.append(f"Weight: {current_weight}/{max_weight} kg\n")
        
        # Volume info
        current_volume = data.get('currentVolume', 0)
        max_volume = data.get('maxVolume', 0)
        commands.append(f"Volume: {current_volume}/{max_volume} m³\n")
        
        # Location info
        location_id = data.get('locationId')
        if location_id:
            commands.append(f"Location ID: {location_id}\n")
        
        # Footer
        commands.append("-" * 32 + "\n")
        commands.append(f"Created: {data.get('createdAt', '')[:19]}\n")
        commands.append(f"Printed: {data.get('printedAt', time.strftime('%Y-%m-%d %H:%M:%S'))}\n")
        
        # Cut paper
        commands.append("\n")
        commands.append(self.CUT)
        
        return "".join(commands)
    
    def generate_test_label(self, data: Dict[str, Any]) -> str:
        """Generate ESC/POS commands for test label"""
        commands = []
        
        # Initialize printer
        commands.append(self.INIT)
        
        # Header
        commands.append(self.ALIGN_CENTER)
        commands.append(self.LARGE_FONT)
        commands.append(self.BOLD_ON)
        commands.append("TEST LABEL\n")
        commands.append(self.BOLD_OFF)
        commands.append(self.NORMAL_FONT)
        commands.append("=" * 20 + "\n")
        
        # Test message
        message = data.get('message', 'Printer Test')
        commands.append(f"{message}\n")
        
        # Timestamp
        timestamp = data.get('timestamp', time.strftime('%Y-%m-%d %H:%M:%S'))
        commands.append(f"Time: {timestamp}\n")
        
        # Footer
        commands.append("=" * 20 + "\n")
        commands.append("Print Test Successful\n")
        
        # Cut paper
        commands.append("\n")
        commands.append(self.CUT)
        
        return "".join(commands)


class ZPLLabelGenerator(LabelGeneratorBase):
    """ZPL (Zebra Programming Language) command generator"""
    
    def generate_location_label(self, data: Dict[str, Any]) -> str:
        """Generate ZPL commands for location label"""
        zpl = []
        
        # Start label
        zpl.append("^XA")
        
        # Set label size (adjust as needed)
        zpl.append("^LH0,0")
        zpl.append("^PW400")
        
        # Title
        zpl.append("^FO50,30")
        zpl.append("^CF0,30")
        zpl.append("^FDLOCATION LABEL^FS")
        
        # Barcode
        barcode = data.get('barcode', '')
        if barcode:
            zpl.append("^FO50,80")
            zpl.append("^BY2,3,50")
            zpl.append(f"^BC^FD{barcode}^FS")
        
        # Location data
        y_pos = 160
        zpl.append(f"^FO50,{y_pos}")
        zpl.append("^CF0,20")
        zpl.append(f"^FDLocation: {data.get('locationName', 'N/A')}^FS")
        
        y_pos += 25
        zpl.append(f"^FO50,{y_pos}")
        zpl.append(f"^FDWarehouse: {data.get('warehouseCode', 'N/A')}^FS")
        
        y_pos += 25
        zpl.append(f"^FO50,{y_pos}")
        zpl.append(f"^FDType: {data.get('locationType', 'N/A')}^FS")
        
        # Position
        aisle = data.get('aisle', '')
        bay = data.get('bay', '')
        level = data.get('level', '')
        if aisle or bay or level:
            y_pos += 25
            zpl.append(f"^FO50,{y_pos}")
            zpl.append(f"^FDPosition: {aisle}-{bay}-{level}^FS")
        
        # Print timestamp
        y_pos += 40
        zpl.append(f"^FO50,{y_pos}")
        zpl.append("^CF0,15")
        zpl.append(f"^FDPrinted: {data.get('printedAt', time.strftime('%Y-%m-%d %H:%M:%S'))}^FS")
        
        # End label
        zpl.append("^XZ")
        
        return "\n".join(zpl)
    
    def generate_pallet_label(self, data: Dict[str, Any]) -> str:
        """Generate ZPL commands for pallet label"""
        zpl = []
        
        # Start label
        zpl.append("^XA")
        
        # Set label size
        zpl.append("^LH0,0")
        zpl.append("^PW400")
        
        # Title
        zpl.append("^FO50,30")
        zpl.append("^CF0,30")
        zpl.append("^FDPALLET LABEL^FS")
        
        # Barcode
        barcode = data.get('barcode', '')
        if barcode:
            zpl.append("^FO50,80")
            zpl.append("^BY2,3,50")
            zpl.append(f"^BC^FD{barcode}^FS")
        
        # Pallet data
        y_pos = 160
        zpl.append(f"^FO50,{y_pos}")
        zpl.append("^CF0,20")
        zpl.append(f"^FDPallet ID: {data.get('id', 'N/A')}^FS")
        
        y_pos += 25
        zpl.append(f"^FO50,{y_pos}")
        zpl.append(f"^FDType: {data.get('palletType', 'N/A')}^FS")
        
        y_pos += 25
        zpl.append(f"^FO50,{y_pos}")
        zpl.append(f"^FDStatus: {data.get('status', 'N/A')}^FS")
        
        # Weight
        current_weight = data.get('currentWeight', 0)
        max_weight = data.get('maxWeight', 0)
        y_pos += 25
        zpl.append(f"^FO50,{y_pos}")
        zpl.append(f"^FDWeight: {current_weight}/{max_weight} kg^FS")
        
        # Print timestamp
        y_pos += 40
        zpl.append(f"^FO50,{y_pos}")
        zpl.append("^CF0,15")
        zpl.append(f"^FDPrinted: {data.get('printedAt', time.strftime('%Y-%m-%d %H:%M:%S'))}^FS")
        
        # End label
        zpl.append("^XZ")
        
        return "\n".join(zpl)
    
    def generate_test_label(self, data: Dict[str, Any]) -> str:
        """Generate ZPL commands for test label"""
        zpl = []
        
        # Start label
        zpl.append("^XA")
        
        # Set label size
        zpl.append("^LH0,0")
        zpl.append("^PW400")
        
        # Title
        zpl.append("^FO100,50")
        zpl.append("^CF0,40")
        zpl.append("^FDTEST LABEL^FS")
        
        # Message
        message = data.get('message', 'Printer Test')
        zpl.append("^FO50,120")
        zpl.append("^CF0,25")
        zpl.append(f"^FD{message}^FS")
        
        # Timestamp
        timestamp = data.get('timestamp', time.strftime('%H:%M:%S'))
        zpl.append("^FO50,160")
        zpl.append("^CF0,20")
        zpl.append(f"^FDTime: {timestamp}^FS")
        
        # End label
        zpl.append("^XZ")
        
        return "\n".join(zpl)


def get_label_generator(printer_type: str = "thermal") -> LabelGeneratorBase:
    """Factory function to get appropriate label generator"""
    if printer_type.lower() in ["thermal", "escpos"]:
        return ESCPOSLabelGenerator()
    elif printer_type.lower() in ["zebra", "zpl"]:
        return ZPLLabelGenerator()
    else:
        # Default to ESC/POS
        return ESCPOSLabelGenerator()
