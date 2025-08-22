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
        """Generate ZPL commands for location label using location.zpl template"""
        import os
        
        # Read the location.zpl template
        template_path = os.path.join(os.path.dirname(__file__), 'location.zpl')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                zpl_template = f.read()
        except FileNotFoundError:
            # Fallback to embedded template if file not found
            zpl_template = """^XA
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
        ^FX start bottom table
        ^CF0,40
        ^FO10,200^FB375,1,0,C^FDAlt Raf^FS
        ^A0N,30,30^FO10,250^FB375,1,0,C^FDDP-S-{i}1^FS
        ^FO90,320
        ^BQN,2,10
        ^FDLA,DP-S-{i}1^FS

        ^CF0,40
        ^FO390,200^FB375,1,0,C^FDÜst Raf^FS
        ^A0N,30,30^FO390,250^FB375,1,0,C^FDDP-S-{i}2^FS
        ^FO470,320
        ^BQN,2,10
        ^FDLA,DP-S-{i}2^FS
        ^FO10,170^GB375,450,2^FS
        ^FO385,170^GB375,450,2^FS
        ^XZ"""
        
        # Extract data for template placeholders
        location_id = data.get('id', data.get('locationId', '1'))
        location_name = data.get('locationName', 'Sevkiyat Ürün Deposu')
        warehouse_code = data.get('warehouseCode', 'Ana Fabrika')
        barcode = data.get('barcode', f'LOC{location_id:06d}')
        
        # Replace placeholders in template
        # {i} placeholder is used for location ID in the template
        zpl_command = zpl_template.replace('{i}', str(location_id))
        
        # If we want to customize company/warehouse info, we can add more replacements
        if 'locationName' in data and data['locationName']:
            # Replace the default location name with actual data
            zpl_command = zpl_command.replace('Sevkiyat Ürün Deposu', location_name)
        
        if 'warehouseCode' in data and data['warehouseCode']:
            # Replace the default warehouse with actual data  
            zpl_command = zpl_command.replace('Ana Fabrika', warehouse_code)
        
        return zpl_command
    
    def generate_pallet_label(self, data: Dict[str, Any]) -> str:
        """Generate ZPL commands for pallet label using the palet.zpl template"""
        import time
        from datetime import datetime
        
        # Get current date for defaults
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Extract data with defaults matching the template placeholders
        firma_adi = data.get('firma_adi', data.get('firma', 'Bil Plastik Ambalaj'))
        depo_adi = data.get('depo_adi', data.get('depo', 'Ana Fabrika'))
        locationId = data.get('locationId', data.get('locationId', 'Sevkiyat Ürün Deposu'))
        barcode = data.get('barcode', data.get('barcode', 'barcode'))
        urun_adi = data.get('urun_adi', data.get('product_name', 'Ürün Adı'))
        teslim_firma = data.get('teslim_firma', data.get('receiving_company', 'Teslim Alınan Firma'))
        siparis_tarihi = data.get('siparis_tarihi', data.get('order_date', current_date))
        palet_id = data.get('palet_id', f'PLT{int(time.time())%10000:04d}')
        lot_no = data.get('lot_no', f'LOT{int(time.time())%1000:03d}')
        durum = data.get('durum', data.get('status', 'HAZIR'))
        brut_kg = data.get('brut_kg', data.get('gross_weight', '25.0'))
        net_kg = data.get('net_kg', data.get('net_weight', '24.5'))
        
        # Read the palet.zpl template
        try:
            with open('./palet.zpl', 'r', encoding='utf-8') as f:
                zpl_template = f.read()
        except FileNotFoundError:
            # Fallback template if file not found
            zpl_template = """^XA
^PW799
^LL630
^CI28
^MMT
^FO10,10^GB750,2,2^FS
^FO10,10^GB2,600,2,B^FS
^FO759,10^GB2,600,2,B^FS
^FO10,618^GB750,2,2^FS
^FO18,25^A0N,25,25^FDFirma Adı / Depo^FS
^FO25,55^A0N,50,50^FD{firma_adi} / {depo_adi}^FS
^FO10,110^GB750,2,2^FS
^FO18,120^A0N,35,35^FD{sevkiyat_bilgisi}^FS
^FO10,160^GB750,2,2^FS
^FO18,170^A0N,42,42^FD{hammadde_ismi}^FS
^FO18,220^A0N,42,42^FD{urun_adi}^FS
^FO10,270^GB750,2,2^FS
^FO10,275^GB750,2,2^FS
^CF0,40
^FO20,300^FDTeslim Alınan Firma - Bölüm: {teslim_firma}^FS
^FO20,350^FDSipariş Tarihi: {siparis_tarihi}^FS
^FO20,400^FDPalet ID: {palet_id}^FS
^FO20,450^FDDurum: {durum}^FS
^FO20,500^FDBrüt KG.: {brut_kg}^FS
^FO20,550^FDNet KG.: {net_kg}^FS
^FO620,470^BQN,2,6^FDLA,{hammadde_ismi}^FS
^FO600,460^GB160,160,2^FS
^XZ"""
        
        # Replace placeholders with actual data
        zpl_command = zpl_template.format(
            firma_adi=firma_adi,
            depo_adi=depo_adi,
            sevkiyat_bilgisi=locationId,
            hammadde_ismi=barcode,
            urun_adi=urun_adi,
            teslim_firma=teslim_firma,
            siparis_tarihi=siparis_tarihi,
            palet_id=palet_id,
            lot_no=lot_no,
            durum=durum,
            brut_kg=brut_kg,
            net_kg=net_kg
        )
        
        return zpl_command
    
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
