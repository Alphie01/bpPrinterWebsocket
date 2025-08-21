"""
PDF Pallet Summary Generator for A5 Format Printing
===================================================

This module generates detailed pallet summaries in A5 PDF format that can be printed
on regular printers. These summaries complement the thermal label printing.

Features:
- A5 format layout (148mm x 210mm)
- Professional PDF formatting
- Detailed item breakdown  
- Turkish language support
- Windows-optimized printing
- Direct printer integration

Author: Copilot
Version: 1.0.0 (PDF-Based)
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import A5
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class PalletPDFGenerator:
    """Generator for A5 PDF pallet summaries with Turkish font support"""
    
    def __init__(self):
        self.page_width, self.page_height = A5
        self.margin = 10 * mm
        
        # Define styles first
        self.styles = getSampleStyleSheet()
        
        # Set default font names
        self.default_font = 'Helvetica'
        self.default_bold_font = 'Helvetica-Bold'
        
        # Try to register Unicode-compatible fonts
        self._register_fonts()
        
        # Custom styles with proper font names
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName=self.default_bold_font
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=8,
            fontName=self.default_bold_font
        )
        
        self.info_style = ParagraphStyle(
            'InfoStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=4,
            fontName=self.default_font
        )
        
        self.table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.default_bold_font),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('FONTNAME', (0, 1), (-1, -1), self.default_font),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])

    def _register_fonts(self):
        """Register Unicode-compatible fonts for Turkish characters"""
        try:
            # Try to register DejaVu fonts (commonly available)
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # Try to find DejaVu fonts on system
            import os
            font_paths = [
                '/System/Library/Fonts/DejaVuSans.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                'C:\\Windows\\Fonts\\DejaVuSans.ttf',  # Windows (if installed)
                '/usr/share/fonts/dejavu/DejaVuSans.ttf',  # Alternative Linux path
            ]
            
            bold_font_paths = [
                '/System/Library/Fonts/DejaVuSans-Bold.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
                'C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf',  # Windows (if installed)
                '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',  # Alternative Linux path
            ]
            
            # Register regular DejaVu font
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('DejaVu', font_path))
                    self.default_font = 'DejaVu'
                    break
            
            # Register bold DejaVu font
            for font_path in bold_font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('DejaVu-Bold', font_path))
                    self.default_bold_font = 'DejaVu-Bold'
                    break
                    
        except Exception as e:
            # If font registration fails, keep using Helvetica
            pass
    
    def _setup_helvetica_fallback(self):
        """Setup Helvetica fonts with better Turkish character support"""
        # This method is no longer needed as we set defaults
        pass

    def generate_pdf_summary(self, pallet_data: Dict[str, Any]) -> str:
        """Generate PDF summary for pallet data"""
        
        # Extract data with fallbacks - updated for new backend format
        # Check if we have the new nested structure
        pallet_info = pallet_data.get('palletInfo', {})
        summary = pallet_data.get('summary', {})
        stock_details = pallet_data.get('stockDetails', [])
        grouped_products = pallet_data.get('groupedProducts', [])
        
        # Extract pallet information
        pallet_id = pallet_info.get('id', pallet_data.get('palet_id', 'UNKNOWN'))
        barcode = pallet_info.get('barcode', pallet_data.get('barcode', ''))
        pallet_type = pallet_info.get('type', 'UNKNOWN')
        status = pallet_info.get('status', pallet_data.get('status', 'UNKNOWN'))
        current_weight = pallet_info.get('currentWeight', pallet_data.get('currentWeight', 0))
        
        # Location information
        location_info = pallet_info.get('location', {})
        warehouse = location_info.get('name', pallet_data.get('warehouse', 'Ana Depo'))
        
        # Company and other info with fallbacks
        company_name = pallet_data.get('firma_adi', pallet_data.get('company_name', 'Bil Plastik Ambalaj'))
        receiving_company = pallet_data.get('teslim_firma', pallet_data.get('receiving_company', '-'))
        order_date = pallet_data.get('printedAt', pallet_data.get('order_date', datetime.now().strftime('%Y-%m-%d')))
        
        # Format order_date if it's ISO format
        try:
            if 'T' in str(order_date):
                from datetime import datetime
                parsed_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                order_date = parsed_date.strftime('%Y-%m-%d %H:%M')
        except:
            pass
        
        # Weight information
        total_weight = float(current_weight)
        net_weight = float(pallet_data.get('net_kg', pallet_data.get('net_weight', total_weight)))
        
        # Summary information
        total_stock_items = summary.get('totalStockItems', len(stock_details))
        total_product_types = summary.get('totalProductTypes', len(grouped_products))
        total_quantity = summary.get('totalQuantity', 0)
        utilization_percentage = summary.get('utilizationPercentage', 0)
        
        # Generate filename
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"pallet_summary_{pallet_id}_{timestamp}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(
            filename,
            pagesize=A5,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Build content with proper Turkish character encoding
        story = []
        
        # Company header
        story.append(Paragraph(self._encode_text(company_name), self.title_style))
        story.append(Paragraph(self._encode_text("PALET ÖZET RAPORU"), self.header_style))
        story.append(Spacer(1, 8))
        
        # Basic information table with encoded text
        basic_info = [
            [self._encode_text('Palet ID:'), str(pallet_id), self._encode_text('Durum:'), self._encode_text(status)],
            [self._encode_text('Barkod:'), str(barcode), self._encode_text('Tip:'), self._encode_text(pallet_type)],
            [self._encode_text('Depo:'), self._encode_text(warehouse), self._encode_text('Tarih:'), str(order_date)],
            [self._encode_text('Toplam Ürün:'), str(total_product_types), self._encode_text('Toplam Stok:'), str(total_stock_items)],
        ]
        
        basic_table = Table(basic_info, colWidths=[25*mm, 35*mm, 20*mm, 30*mm])
        basic_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ]))
        
        story.append(basic_table)
        story.append(Spacer(1, 10))
        
        # Weight and summary information
        story.append(Paragraph(self._encode_text("AĞIRLIK VE ÖZET BİLGİLERİ"), self.header_style))
        
        weight_info = [
            [self._encode_text('Toplam Ağırlık:'), f"{total_weight:.2f} kg"],
            [self._encode_text('Toplam Miktar:'), f"{total_quantity}"],
            [self._encode_text('Kullanım Oranı:'), f"{utilization_percentage:.1f}%"],
        ]
        
        weight_table = Table(weight_info, colWidths=[40*mm, 30*mm])
        weight_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        
        story.append(weight_table)
        story.append(Spacer(1, 10))
        
        # Grouped products summary
        if grouped_products:
            story.append(Paragraph(self._encode_text("ÜRÜN GRUPLARI ÖZETİ"), self.header_style))
            
            # Products table with encoded headers
            products_data = [[
                self._encode_text('Ürün Kodu'), 
                self._encode_text('Birim'), 
                self._encode_text('Toplam Miktar'),
                self._encode_text('Stok Sayısı')
            ]]
            
            for product in grouped_products:
                product_code = product.get('productCode', '-')
                unit = product.get('unit', '-')
                total_qty = product.get('totalQuantity', 0)
                stock_count = product.get('stockCount', 0)
                
                products_data.append([
                    self._encode_text(str(product_code)), 
                    str(unit), 
                    str(total_qty),
                    str(stock_count)
                ])
            
            products_table = Table(products_data, colWidths=[30*mm, 20*mm, 25*mm, 25*mm])
            products_table.setStyle(self.table_style)
            story.append(products_table)
            story.append(Spacer(1, 10))
        
        # Detailed stock information (limited to first 5 items to save space)
        if stock_details:
            story.append(Paragraph(self._encode_text("DETAYЛИ STOK BİLGİLERİ"), self.header_style))
            
            # Stock details table with encoded headers
            stock_data = [[
                self._encode_text('Ürün Kodu'), 
                self._encode_text('Lot No'), 
                self._encode_text('Miktar'),
                self._encode_text('Durum')
            ]]
            
            # Show only first 5 items to keep PDF readable
            for stock in stock_details[:5]:
                product_code = stock.get('productCode', '-')
                lot_number = stock.get('lotNumber', '-')
                quantity = stock.get('quantity', 0)
                unit = stock.get('unit', '')
                stock_status = stock.get('status', '-')
                
                stock_data.append([
                    self._encode_text(str(product_code)), 
                    str(lot_number), 
                    f"{quantity} {unit}",
                    self._encode_text(str(stock_status))
                ])
            
            # Add note if there are more items
            if len(stock_details) > 5:
                stock_data.append([
                    self._encode_text(f"... ve {len(stock_details) - 5} adet daha"), 
                    '', '', ''
                ])
            
            stock_table = Table(stock_data, colWidths=[25*mm, 25*mm, 25*mm, 25*mm])
            stock_table.setStyle(self.table_style)
            story.append(stock_table)
        
        # Additional info with encoded text
        story.append(Spacer(1, 15))
        story.append(Paragraph("─" * 50, self.info_style))
        story.append(Paragraph(
            self._encode_text(f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}"), 
            self.info_style
        ))
        story.append(Paragraph(
            self._encode_text("Bu rapor otomatik olarak oluşturulmuştur."), 
            self.info_style
        ))
        
        # Build PDF
        doc.build(story)
        
        return os.path.abspath(filename)

    def _encode_text(self, text: str) -> str:
        """Encode Turkish characters for PDF compatibility"""
        if not text:
            return ""
        
        # Use ReportLab's built-in encoding support
        try:
            # For ReportLab, we can use unicode directly if we escape special characters
            # and rely on font handling
            
            # Simple character replacement for better compatibility
            replacements = {
                'ç': 'c',
                'Ç': 'C', 
                'ğ': 'g',
                'Ğ': 'G',
                'ı': 'i',
                'İ': 'I',
                'ö': 'o',
                'Ö': 'O',
                'ş': 's',
                'Ş': 'S',
                'ü': 'u',
                'Ü': 'U'
            }
            
            # Use unicode with fallback to ASCII replacements
            encoded = text
            
            # If we have unicode support, try to preserve original
            try:
                encoded.encode('latin-1')
                return encoded  # Can be encoded in latin-1, should work
            except UnicodeEncodeError:
                # Fall back to character replacement
                for turkish, replacement in replacements.items():
                    encoded = encoded.replace(turkish, replacement)
                return encoded
                
        except Exception:
            # Ultimate fallback - just return as-is
            return text


def get_pdf_pallet_generator() -> PalletPDFGenerator:
    """Factory function to get PDF pallet generator"""
    return PalletPDFGenerator()
