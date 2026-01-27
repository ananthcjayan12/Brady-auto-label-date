import os
import logging
import re
import uuid
import platform
import subprocess
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
# DataMatrix in reportlab requires 'reportlab' version >= 3.x
from reportlab.graphics.barcode import createBarcodeDrawing

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
        # Default Settings
        default_settings = {
            'labelWidth': 50, # mm
            'labelHeight': 25, # mm
            'fontSize': 8,
            'qrSize': 15, # mm
        }
        
        s = {**default_settings, **(settings or {})}
        
        filename = f"batch_{uuid.uuid4().hex}.pdf"
        file_path = os.path.join(self.output_folder, filename)
        
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
                printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
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
        Sends the generated PDF to the printer.
        """
        system = platform.system()
        
        try:
            if system == 'Windows':
                if not printer_name:
                    import win32print
                    printer_name = win32print.GetDefaultPrinter()

                cmd = [
                    'powershell', 
                    '-Command', 
                    f'Start-Process -FilePath "{file_path}" -Verb PrintTo -ArgumentList "{printer_name}" -PassThru -Wait'
                ]
                subprocess.run(cmd, check=True)
                return True, "Sent to Windows Printer"
            
            else:
                # Mac/Linux LPR
                cmd = ['lpr']
                if printer_name:
                    cmd.extend(['-P', printer_name])
                cmd.append(file_path)
                subprocess.run(cmd, check=True)
                return True, "Sent to Unix Printer"

        except Exception as e:
            return False, str(e)