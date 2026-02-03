import os
import logging
import re
import uuid
import platform
import subprocess
import sys
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

import qrcode
from io import BytesIO

# --- NEW SERVICE: Handles Brady Label Creation ---
class BradyLabelService:
    def __init__(self, output_folder):
        self.output_folder = output_folder

    def generate_batch(self, system_name, year, month, start_serial, quantity, settings=None):
        """
        Generates a combined PDF with multiple labels.
        """
        # Default Settings - 100mm x 35mm Brady Labels
        default_settings = {
            'labelWidth': 100, # mm (landscape)
            'labelHeight': 35, # mm
            'fontSize': 12,
            'qrSize': 25, # mm
        }
        
        s = {**default_settings, **(settings or {})}
        
        filename = f"batch_{uuid.uuid4().hex}.pdf"
        file_path = os.path.join(self.output_folder, filename)
        
        # Create PDF in landscape orientation: 100mm x 35mm
        # Printer settings (paper size, orientation) are set programmatically in print_file()
        c = canvas.Canvas(file_path, pagesize=(s['labelWidth']*mm, s['labelHeight']*mm))
        
        padding = len(start_serial)
        start_num = int(start_serial)

        for i in range(quantity):
            current_serial = str(start_num + i).zfill(padding)
            label_content = f"{year}{month}{current_serial}"
            
            self._draw_single_label(c, system_name, label_content, s)
            c.showPage()
        
        c.save()
        return file_path

    def _draw_single_label(self, c, system_name, content, s):
        """
        Draws a single label on the current canvas page.
        """
        # Generate QR Code using 'qrcode' library
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to a memory buffer
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Draw image on canvas
        from reportlab.lib.utils import ImageReader
        logo = ImageReader(img_buffer)
        
        # Center QR code
        qr_x = (s['labelWidth'] - s['qrSize']) / 2 * mm
        qr_y = (s['labelHeight'] - s['qrSize'] + 2) / 2 * mm
        c.drawImage(logo, qr_x, qr_y, width=s['qrSize']*mm, height=s['qrSize']*mm)
        
        # Text at bottom
        # Try to use Arial if registered, otherwise Helvetica
        try:
            c.setFont("Arial", s['fontSize'])
        except:
            c.setFont("Helvetica-Bold", s['fontSize'])

        text_width = c.stringWidth(content, "Helvetica-Bold" if "Helvetica" in c._fontname else "Arial", s['fontSize'])
        text_x = (s['labelWidth']*mm - text_width) / 2
        c.drawString(text_x, 2*mm, content)

    def generate_label(self, system_name, year, month, serial, settings=None):
        """
        Compatibility method for single label generation.
        """
        return self.generate_batch(system_name, year, month, serial, 1, settings)


# --- REUSED SERVICE: Handles Printing ---
class PrintService:
    def get_available_printers(self):
        """Reused Logic from previous project"""
        printers = []
        default_printer = None
        system = platform.system()
        
        try:
            if system == 'Windows':
                import win32print
                for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS):
                    printers.append(printer[2])
                default_printer = win32print.GetDefaultPrinter()
            else:
                # Mac/Linux Logic
                result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if line.startswith('printer'):
                        printers.append(line.split()[1])
        except Exception as e:
            logger.error(f"Printer list error: {e}")
            
        return {'printers': printers, 'default': default_printer}

    def print_file(self, file_path, printer_name=None):
        """
        Sends the generated PDF directly to the printer with precise control over
        paper size and orientation using win32print APIs.
        """
        system = platform.system()
        try:
            if system == 'Windows':
                import win32print
                import win32ui
                import win32con
                from PIL import Image
                import fitz  # PyMuPDF

                if not printer_name:
                    printer_name = win32print.GetDefaultPrinter()

                # Convert PDF to image using PyMuPDF (no Poppler needed!)
                pdf_document = fitz.open(file_path)
                page = pdf_document[0]  # Get first page
                
                # Render at high DPI for quality
                mat = fitz.Matrix(300/72, 300/72)  # 300 DPI
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("ppm")
                image = Image.open(BytesIO(img_data))
                pdf_document.close()
                
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Get printer device context
                hDC = win32ui.CreateDC()
                hDC.CreatePrinterDC(printer_name)
                
                # Get printer handle for configuration
                printer_handle = win32print.OpenPrinter(printer_name)
                
                try:
                    # Get current printer settings
                    properties = win32print.GetPrinter(printer_handle, 2)
                    pDevMode = properties["pDevMode"]
                    
                    # Set custom paper size: 100mm x 35mm (landscape label)
                    # Windows uses 0.1mm units, so 100mm = 1000, 35mm = 350
                    pDevMode.PaperWidth = 1000   # 100mm in 0.1mm units
                    pDevMode.PaperLength = 350   # 35mm in 0.1mm units
                    pDevMode.PaperSize = win32con.DMPAPER_USER  # Custom size
                    pDevMode.Orientation = win32con.DMORIENT_LANDSCAPE
                    
                    # Apply settings
                    win32print.SetPrinter(printer_handle, 2, properties, 0)
                    
                finally:
                    win32print.ClosePrinter(printer_handle)
                
                # Get printable area with our custom settings
                printable_area = (
                    hDC.GetDeviceCaps(win32con.HORZRES),
                    hDC.GetDeviceCaps(win32con.VERTRES)
                )
                
                # Scale image to fit printable area
                ratio = min(printable_area[0] / image.size[0], printable_area[1] / image.size[1])
                scaled_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                
                # Center the image
                x = (printable_area[0] - scaled_size[0]) // 2
                y = (printable_area[1] - scaled_size[1]) // 2
                
                # Start print job
                hDC.StartDoc(os.path.basename(file_path))
                hDC.StartPage()
                
                # Draw image to printer
                from PIL import ImageWin
                dib = ImageWin.Dib(image.resize(scaled_size, Image.Resampling.LANCZOS))
                dib.draw(hDC.GetHandleOutput(), (x, y, x + scaled_size[0], y + scaled_size[1]))
                
                hDC.EndPage()
                hDC.EndDoc()
                hDC.DeleteDC()

                return True, f"Printed to {printer_name} with 100x35mm label settings"
            
            else:
                # Mac/Linux Logic
                cmd = ['lpr']
                if printer_name:
                    cmd.extend(['-P', printer_name])
                cmd.append(file_path)
                subprocess.run(cmd, check=True)
                return True, "Sent to Unix Printer"

        except Exception as e:
            logger.error(f"Printing error: {e}")
            return False, str(e)