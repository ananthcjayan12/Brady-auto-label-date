import os
import logging
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Import the new service logic
from services import BradyLabelService, PrintService
from database import DatabaseService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
TEMP_FOLDER = os.path.join(os.path.dirname(__file__), 'temp_labels')
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Initialize Services
label_service = BradyLabelService(output_folder=TEMP_FOLDER)
print_service = PrintService()
db_service = DatabaseService()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Brady Auto Label System is running'})

@app.route('/api/systems', methods=['GET'])
def get_systems():
    """Return list of available systems"""
    return jsonify(['System A', 'System B', 'System C'])

@app.route('/api/printers', methods=['GET'])
def list_printers():
    return jsonify(print_service.get_available_printers())

@app.route('/api/check-duplicates', methods=['POST'])
def check_duplicates():
    data = request.json
    system_name = data.get('system_name')
    year = data.get('year')
    month = data.get('month')
    start_serial = data.get('start_serial')
    quantity = int(data.get('quantity', 1))

    if not all([system_name, year, month, start_serial]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    try:
        duplicates = db_service.check_duplicates(system_name, year, month, start_serial, quantity)
        return jsonify({
            'success': True,
            'has_duplicates': len(duplicates) > 0,
            'duplicates': duplicates
        })
    except Exception as e:
        logger.error(f"Duplicate check error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-batch', methods=['POST'])
def generate_batch():
    data = request.json
    system_name = data.get('system_name')
    year = data.get('year')
    month = data.get('month')
    start_serial = data.get('start_serial')
    quantity = int(data.get('quantity', 1))
    settings = data.get('label_settings')

    if not all([system_name, year, month, start_serial]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    try:
        # 1. Double check duplicates just in case
        duplicates = db_service.check_duplicates(system_name, year, month, start_serial, quantity)
        if duplicates:
            return jsonify({
                'success': False, 
                'error': f"Duplicate serial numbers detected: {', '.join(duplicates)}"
            }), 400

        # 2. Generate the PDF
        pdf_path = label_service.generate_batch(system_name, year, month, start_serial, quantity, settings)
        filename = os.path.basename(pdf_path)

        # 3. Record in database
        db_service.record_prints(system_name, year, month, start_serial, quantity)

        return jsonify({
            'success': True,
            'message': f'Generated batch of {quantity} labels',
            'pdf_url': f"/api/label/{filename}"
        })

    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/label/<filename>', methods=['GET'])
def get_label(filename):
    file_path = os.path.join(TEMP_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'error': 'Label not found'}), 404
    return send_file(file_path, mimetype='application/pdf')

@app.route('/api/print-label', methods=['POST'])
def print_label():
    data = request.json
    pdf_url = data.get('pdf_url', '')
    printer_name = data.get('printer_name')

    if not pdf_url:
        return jsonify({'success': False, 'error': 'No PDF URL provided'}), 400

    try:
        filename = pdf_url.split('/')[-1]
        pdf_path = os.path.join(TEMP_FOLDER, filename)
        
        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'error': 'Label file not found on server'}), 404

        success, message = print_service.print_file(pdf_path, printer_name)

        if success:
            return jsonify({'success': True, 'message': 'Label sent to printer'})
        else:
            return jsonify({'success': False, 'error': f"Printing failed: {message}"}), 500

    except Exception as e:
        logger.error(f"Print error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

