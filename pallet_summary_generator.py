"""
Pallet Summary Generator for A5 Format Printing
===============================================

This module generates detailed pallet summaries in A5 format that can be printed
on regular printers. These summaries complement the thermal label printing.

Features:
- A5 format layout (148mm x 210mm)
- Detailed item breakdown
- Turkish language support
- Both HTML and plain text formats
- Print-ready formatting

Author: Copilot
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class PalletItem:
    """Individual item on the pallet"""
    product_code: str
    product_name: str
    quantity: int
    unit: str
    weight_per_unit: float
    total_weight: float
    lot_number: Optional[str] = None
    production_date: Optional[str] = None


@dataclass
class PalletSummary:
    """Complete pallet summary data"""
    pallet_id: str
    company_name: str
    warehouse: str
    receiving_company: str
    order_date: str
    total_items: int
    total_weight: float
    net_weight: float
    status: str
    items: List[PalletItem]
    created_by: Optional[str] = None
    notes: Optional[str] = None


class PalletSummaryGenerator:
    """Generator for A5 format pallet summaries"""
    
    # A5 dimensions in characters (approximately 80 characters wide for 10pt font)
    LINE_WIDTH = 80
    PAGE_HEIGHT = 60  # lines
    
    def __init__(self):
        self.current_date = datetime.now()
    
    def generate_html_summary(self, pallet_data: Dict[str, Any]) -> str:
        """Generate HTML format pallet summary for A5 printing"""
        summary = self._parse_pallet_data(pallet_data)
        
        html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Palet Özet Raporu - {summary.pallet_id}</title>
    <style>
        @page {{
            size: A5;
            margin: 15mm;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            font-size: 10pt;
            line-height: 1.2;
            margin: 0;
            padding: 0;
            color: #333;
        }}
        
        .header {{
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        
        .company-name {{
            font-size: 14pt;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .report-title {{
            font-size: 12pt;
            font-weight: bold;
            color: #666;
        }}
        
        .info-section {{
            margin-bottom: 15px;
        }}
        
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 10px;
        }}
        
        .info-table td {{
            padding: 3px 5px;
            border: 1px solid #ddd;
            font-size: 9pt;
        }}
        
        .info-table .label {{
            background-color: #f5f5f5;
            font-weight: bold;
            width: 40%;
        }}
        
        .items-section {{
            margin-bottom: 15px;
        }}
        
        .items-title {{
            font-size: 11pt;
            font-weight: bold;
            margin-bottom: 10px;
            border-bottom: 1px solid #333;
            padding-bottom: 3px;
        }}
        
        .items-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 8pt;
        }}
        
        .items-table th {{
            background-color: #333;
            color: white;
            padding: 4px 2px;
            text-align: left;
            font-weight: bold;
        }}
        
        .items-table td {{
            padding: 3px 2px;
            border: 1px solid #ddd;
        }}
        
        .items-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        .summary-section {{
            border-top: 2px solid #333;
            padding-top: 10px;
            margin-top: 15px;
        }}
        
        .summary-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .summary-table td {{
            padding: 4px 5px;
            font-weight: bold;
        }}
        
        .summary-table .total-row {{
            background-color: #333;
            color: white;
        }}
        
        .footer {{
            margin-top: 15px;
            text-align: center;
            font-size: 8pt;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 5px;
        }}
        
        .status {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 9pt;
        }}
        
        .status.ready {{
            background-color: #4CAF50;
            color: white;
        }}
        
        .status.pending {{
            background-color: #FF9800;
            color: white;
        }}
        
        .status.shipped {{
            background-color: #2196F3;
            color: white;
        }}
        
        @media print {{
            body {{ -webkit-print-color-adjust: exact; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="company-name">{summary.company_name}</div>
        <div class="report-title">PALET ÖZET RAPORU</div>
    </div>
    
    <div class="info-section">
        <table class="info-table">
            <tr>
                <td class="label">Palet ID:</td>
                <td>{summary.pallet_id}</td>
                <td class="label">Durum:</td>
                <td><span class="status {self._get_status_class(summary.status)}">{summary.status}</span></td>
            </tr>
            <tr>
                <td class="label">Depo:</td>
                <td>{summary.warehouse}</td>
                <td class="label">Sipariş Tarihi:</td>
                <td>{summary.order_date}</td>
            </tr>
            <tr>
                <td class="label">Teslim Alacak Firma:</td>
                <td colspan="3">{summary.receiving_company}</td>
            </tr>
        </table>
    </div>
    
    <div class="items-section">
        <div class="items-title">Palet İçeriği ({summary.total_items} Kalem)</div>
        <table class="items-table">
            <thead>
                <tr>
                    <th style="width: 15%;">Ürün Kodu</th>
                    <th style="width: 35%;">Ürün Adı</th>
                    <th style="width: 10%;">Adet</th>
                    <th style="width: 8%;">Birim</th>
                    <th style="width: 12%;">Birim Ağırlık</th>
                    <th style="width: 12%;">Toplam Ağırlık</th>
                    <th style="width: 8%;">Lot No</th>
                </tr>
            </thead>
            <tbody>
        """
        
        # Add items
        for item in summary.items:
            html += f"""
                <tr>
                    <td>{item.product_code}</td>
                    <td>{item.product_name}</td>
                    <td style="text-align: right;">{item.quantity}</td>
                    <td>{item.unit}</td>
                    <td style="text-align: right;">{item.weight_per_unit:.2f} kg</td>
                    <td style="text-align: right;">{item.total_weight:.2f} kg</td>
                    <td>{item.lot_number or '-'}</td>
                </tr>
            """
        
        html += f"""
            </tbody>
        </table>
    </div>
    
    <div class="summary-section">
        <table class="summary-table">
            <tr class="total-row">
                <td>TOPLAM ÜRÜN ADEDI:</td>
                <td style="text-align: right;">{summary.total_items} Kalem</td>
                <td>BRÜT AĞIRLIK:</td>
                <td style="text-align: right;">{summary.total_weight:.2f} kg</td>
            </tr>
            <tr>
                <td style="background-color: #f5f5f5;">NET AĞIRLIK:</td>
                <td style="text-align: right; background-color: #f5f5f5;">{summary.net_weight:.2f} kg</td>
                <td style="background-color: #f5f5f5;">DARA AĞIRLIĞI:</td>
                <td style="text-align: right; background-color: #f5f5f5;">{summary.total_weight - summary.net_weight:.2f} kg</td>
            </tr>
        </table>
    </div>
    
    <div class="footer">
        <p>Rapor Tarihi: {self.current_date.strftime('%d.%m.%Y %H:%M:%S')}</p>
        {f'<p>Hazırlayan: {summary.created_by}</p>' if summary.created_by else ''}
        {f'<p>Not: {summary.notes}</p>' if summary.notes else ''}
        <p>Bu belge bilgisayar ortamında oluşturulmuştur.</p>
    </div>
</body>
</html>
        """
        
        return html.strip()
    
    def generate_text_summary(self, pallet_data: Dict[str, Any]) -> str:
        """Generate plain text format pallet summary for basic printers"""
        summary = self._parse_pallet_data(pallet_data)
        
        lines = []
        
        # Header
        lines.append("=" * self.LINE_WIDTH)
        lines.append(summary.company_name.center(self.LINE_WIDTH))
        lines.append("PALET ÖZET RAPORU".center(self.LINE_WIDTH))
        lines.append("=" * self.LINE_WIDTH)
        lines.append("")
        
        # Basic info
        lines.append(f"Palet ID: {summary.pallet_id}".ljust(40) + f"Durum: {summary.status}")
        lines.append(f"Depo: {summary.warehouse}".ljust(40) + f"Sipariş Tarihi: {summary.order_date}")
        lines.append(f"Teslim Alacak Firma: {summary.receiving_company}")
        lines.append("")
        lines.append("-" * self.LINE_WIDTH)
        
        # Items header
        lines.append(f"PALET İÇERİĞİ ({summary.total_items} Kalem)")
        lines.append("-" * self.LINE_WIDTH)
        
        # Items table header
        header = f"{'Kod':<12} {'Ürün Adı':<25} {'Adet':<6} {'Birim':<6} {'B.Ağ.':<8} {'T.Ağ.':<8} {'Lot':<8}"
        lines.append(header)
        lines.append("-" * self.LINE_WIDTH)
        
        # Items
        for item in summary.items:
            line = (f"{item.product_code:<12} "
                   f"{item.product_name[:25]:<25} "
                   f"{item.quantity:<6} "
                   f"{item.unit:<6} "
                   f"{item.weight_per_unit:<8.2f} "
                   f"{item.total_weight:<8.2f} "
                   f"{(item.lot_number or '-')[:8]:<8}")
            lines.append(line)
        
        # Summary
        lines.append("-" * self.LINE_WIDTH)
        lines.append(f"TOPLAM KALEM: {summary.total_items}".ljust(40) + f"BRÜT AĞIRLIK: {summary.total_weight:.2f} kg")
        lines.append(f"NET AĞIRLIK: {summary.net_weight:.2f} kg".ljust(40) + f"DARA: {summary.total_weight - summary.net_weight:.2f} kg")
        lines.append("=" * self.LINE_WIDTH)
        
        # Footer
        lines.append("")
        lines.append(f"Rapor Tarihi: {self.current_date.strftime('%d.%m.%Y %H:%M:%S')}")
        if summary.created_by:
            lines.append(f"Hazırlayan: {summary.created_by}")
        if summary.notes:
            lines.append(f"Not: {summary.notes}")
        
        return "\n".join(lines)
    
    def _parse_pallet_data(self, data: Dict[str, Any]) -> PalletSummary:
        """Parse pallet data into structured format"""
        # Extract basic pallet info
        pallet_id = data.get('palet_id', data.get('pallet_id', f'PLT{int(time.time())%10000:04d}'))
        company_name = data.get('firma_adi', data.get('company_name', 'Bil Plastik Ambalaj'))
        warehouse = data.get('depo_adi', data.get('warehouse', 'Ana Fabrika'))
        receiving_company = data.get('teslim_firma', data.get('receiving_company', 'Müşteri Firması'))
        order_date = data.get('siparis_tarihi', data.get('order_date', datetime.now().strftime('%Y-%m-%d')))
        status = data.get('durum', data.get('status', 'HAZIR'))
        total_weight = float(data.get('brut_kg', data.get('gross_weight', 25.0)))
        net_weight = float(data.get('net_kg', data.get('net_weight', 24.5)))
        
        # Parse items from various possible formats
        items = []
        items_data = data.get('items', data.get('pallet_items', []))
        
        if items_data:
            # If explicit items list provided
            for item_data in items_data:
                item = PalletItem(
                    product_code=item_data.get('product_code', item_data.get('kod', 'ÜRÜN001')),
                    product_name=item_data.get('product_name', item_data.get('ad', 'Ürün Adı')),
                    quantity=int(item_data.get('quantity', item_data.get('adet', 1))),
                    unit=item_data.get('unit', item_data.get('birim', 'adet')),
                    weight_per_unit=float(item_data.get('weight_per_unit', item_data.get('birim_agirlik', 1.0))),
                    total_weight=float(item_data.get('total_weight', item_data.get('toplam_agirlik', 1.0))),
                    lot_number=item_data.get('lot_number', item_data.get('lot_no')),
                    production_date=item_data.get('production_date', item_data.get('uretim_tarihi'))
                )
                items.append(item)
        else:
            # Generate default item from main product info if no items list
            product_name = data.get('hammadde_ismi', data.get('urun_adi', data.get('product_name', 'Hammadde')))
            
            item = PalletItem(
                product_code=data.get('product_code', 'HMMD001'),
                product_name=product_name,
                quantity=1,
                unit='palet',
                weight_per_unit=net_weight,
                total_weight=total_weight,
                lot_number=data.get('lot_no'),
                production_date=data.get('production_date')
            )
            items.append(item)
        
        return PalletSummary(
            pallet_id=pallet_id,
            company_name=company_name,
            warehouse=warehouse,
            receiving_company=receiving_company,
            order_date=order_date,
            total_items=len(items),
            total_weight=total_weight,
            net_weight=net_weight,
            status=status,
            items=items,
            created_by=data.get('created_by', data.get('operator')),
            notes=data.get('notes', data.get('notlar'))
        )
    
    def _get_status_class(self, status: str) -> str:
        """Get CSS class for status"""
        status_lower = status.lower()
        if status_lower in ['hazır', 'ready', 'completed']:
            return 'ready'
        elif status_lower in ['beklemede', 'pending', 'processing']:
            return 'pending'
        elif status_lower in ['sevk edildi', 'shipped', 'delivered']:
            return 'shipped'
        else:
            return 'pending'


def get_pallet_summary_generator() -> PalletSummaryGenerator:
    """Factory function to get pallet summary generator"""
    return PalletSummaryGenerator()
