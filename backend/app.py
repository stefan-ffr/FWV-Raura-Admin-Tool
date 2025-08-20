from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Create upload folder if it doesn't exist
os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
os.makedirs(os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'receipts'), exist_ok=True)
os.makedirs(os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'qr_invoices'), exist_ok=True)

def get_db():
    """Create database connection"""
    try:
        return mysql.connector.connect(
            host=app.config.get('MYSQL_HOST', 'localhost'),
            user=app.config.get('MYSQL_USER', 'root'),
            password=app.config.get('MYSQL_PASSWORD', ''),
            database=app.config.get('MYSQL_DATABASE', 'fwv_raura')
        )
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'FWV Raura API'}), 200

@app.route('/api/register', methods=['POST'])
def register_member():
    """Public registration endpoint"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'phone1']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # For now, just return success (implement DB later)
        return jsonify({
            'success': True, 
            'message': 'Registration received',
            'member_id': str(uuid.uuid4())
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/members', methods=['GET'])
def get_members():
    """Get all members (admin only)"""
    try:
        # Mock data for now
        members = [
            {
                'id': 1,
                'first_name': 'Max',
                'last_name': 'Muster',
                'email': 'max.muster@example.ch',
                'phone1': '+41791234567',
                'status': 'approved'
            }
        ]
        return jsonify(members), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard statistics"""
    try:
        # Mock data for now
        return jsonify({
            'memberCount': 42,
            'pendingRegistrations': 3,
            'pendingReimbursements': 2,
            'openInvoices': 5
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reimbursement', methods=['POST'])
def submit_reimbursement():
    """Submit reimbursement request"""
    try:
        email = request.form.get('email')
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        
        # Handle file upload if present
        receipt_path = None
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file and file.filename:
                filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
                receipt_path = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'receipts', filename)
                file.save(receipt_path)
        
        # Generate reference number
        reference = f"GS{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:4].upper()}"
        
        return jsonify({
            'success': True,
            'reimbursement_id': str(uuid.uuid4()),
            'reference': reference,
            'message': 'Reimbursement submitted successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
