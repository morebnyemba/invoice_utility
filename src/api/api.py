"""
REST API Module for Invoice Utility
Provides HTTP endpoints for integration with external systems
"""
from flask import Flask, request, jsonify, send_file
from functools import wraps
import jwt
import datetime
import os
from typing import Dict, List, Optional
import io

# Import database and business logic
try:
    from src.models.database import get_db_connection
    from src.business.business_logic import TaxCalculator, CurrencyConverter
except ImportError:
    print("Warning: Database or business_logic modules not available")

# Flask app initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('API_SECRET_KEY', 'change-this-in-production')

# ---------- AUTHENTICATION ----------

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Key')
        
        if not token:
            return jsonify({'error': 'API key is missing'}), 401
        
        # Verify API key against database
        try:
            with get_db_connection() as conn:
                api_key = conn.execute(
                    "SELECT * FROM api_keys WHERE key = ? AND is_active = 1",
                    (token,)
                ).fetchone()
                
                if not api_key:
                    return jsonify({'error': 'Invalid API key'}), 401
                
                # Store API key info for use in endpoint
                request.api_key_info = dict(api_key)
        except Exception as e:
            return jsonify({'error': 'Authentication failed', 'details': str(e)}), 500
        
        return f(*args, **kwargs)
    return decorated

# ---------- CLIENT ENDPOINTS ----------

@app.route('/api/v1/clients', methods=['GET'])
@require_api_key
def get_clients():
    """Get all clients"""
    try:
        with get_db_connection() as conn:
            clients = conn.execute("SELECT * FROM clients ORDER BY name ASC").fetchall()
            return jsonify({
                'success': True,
                'data': [dict(client) for client in clients],
                'count': len(clients)
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/clients/<client_id>', methods=['GET'])
@require_api_key
def get_client(client_id):
    """Get a specific client"""
    try:
        with get_db_connection() as conn:
            client = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
            if not client:
                return jsonify({'success': False, 'error': 'Client not found'}), 404
            return jsonify({'success': True, 'data': dict(client)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/clients', methods=['POST'])
@require_api_key
def create_client():
    """Create a new client"""
    try:
        data = request.get_json()
        required_fields = ['name']
        
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        import uuid
        client_id = str(uuid.uuid4())[:8].upper()
        created_at = datetime.datetime.now().isoformat()
        
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO clients (id, name, email, phone, created_at) VALUES (?, ?, ?, ?, ?)",
                (client_id, data['name'], data.get('email'), data.get('phone'), created_at)
            )
            conn.commit()
        
        return jsonify({'success': True, 'data': {'id': client_id}}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------- INVOICE ENDPOINTS ----------

@app.route('/api/v1/invoices', methods=['GET'])
@require_api_key
def get_invoices():
    """Get all invoices with optional filters"""
    try:
        status = request.args.get('status')
        client_id = request.args.get('client_id')
        
        query = """
            SELECT i.*, c.name as client_name, c.email as client_email 
            FROM invoices i 
            JOIN clients c ON i.client_id = c.id 
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND i.status = ?"
            params.append(status)
        
        if client_id:
            query += " AND i.client_id = ?"
            params.append(client_id)
        
        query += " ORDER BY i.date DESC"
        
        with get_db_connection() as conn:
            invoices = conn.execute(query, tuple(params)).fetchall()
            return jsonify({
                'success': True,
                'data': [dict(inv) for inv in invoices],
                'count': len(invoices)
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/invoices/<invoice_id>', methods=['GET'])
@require_api_key
def get_invoice(invoice_id):
    """Get a specific invoice"""
    try:
        with get_db_connection() as conn:
            invoice = conn.execute("""
                SELECT i.*, c.name as client_name, c.email as client_email, c.phone as client_phone
                FROM invoices i
                JOIN clients c ON i.client_id = c.id
                WHERE i.id = ?
            """, (invoice_id,)).fetchone()
            
            if not invoice:
                return jsonify({'success': False, 'error': 'Invoice not found'}), 404
            
            return jsonify({'success': True, 'data': dict(invoice)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/invoices', methods=['POST'])
@require_api_key
def create_invoice():
    """Create a new invoice"""
    try:
        data = request.get_json()
        required_fields = ['client_id', 'services', 'total', 'date']
        
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        import uuid
        invoice_id = f"ST-{str(uuid.uuid4())[:6].upper()}"
        created_at = datetime.datetime.now().isoformat()
        
        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO invoices (id, client_id, project_id, services, total, date, status, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (invoice_id, data['client_id'], data.get('project_id'), 
                 str(data['services']), data['total'], data['date'], 
                 data.get('status', 'unpaid'), created_at)
            )
            conn.commit()
        
        return jsonify({'success': True, 'data': {'id': invoice_id}}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/invoices/<invoice_id>/pdf', methods=['GET'])
@require_api_key
def get_invoice_pdf(invoice_id):
    """Generate and return invoice PDF"""
    try:
        with get_db_connection() as conn:
            invoice = conn.execute("""
                SELECT i.*, c.name, c.email, c.phone
                FROM invoices i
                JOIN clients c ON i.client_id = c.id
                WHERE i.id = ?
            """, (invoice_id,)).fetchone()
            
            if not invoice:
                return jsonify({'success': False, 'error': 'Invoice not found'}), 404
            
            settings = conn.execute("SELECT key, value FROM settings").fetchall()
            settings_dict = {row['key']: row['value'] for row in settings}
        
        # Generate PDF (using existing function)
        from app import generate_invoice_pdf
        pdf_file = generate_invoice_pdf(dict(invoice), settings_dict)
        
        return send_file(pdf_file, mimetype='application/pdf', as_attachment=True,
                        download_name=f'invoice_{invoice_id}.pdf')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------- PAYMENT ENDPOINTS ----------

@app.route('/api/v1/payments', methods=['POST'])
@require_api_key
def record_payment():
    """Record a payment for an invoice"""
    try:
        data = request.get_json()
        required_fields = ['invoice_id', 'amount', 'date', 'method']
        
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        import uuid
        payment_id = str(uuid.uuid4())[:8]
        created_at = datetime.datetime.now().isoformat()
        
        with get_db_connection() as conn:
            # Record payment
            conn.execute(
                """INSERT INTO payments (id, invoice_id, amount, date, method, notes, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (payment_id, data['invoice_id'], data['amount'], data['date'], 
                 data['method'], data.get('notes', ''), created_at)
            )
            
            # Update invoice status
            invoice = conn.execute("SELECT total FROM invoices WHERE id = ?", 
                                  (data['invoice_id'],)).fetchone()
            total_paid = conn.execute("SELECT SUM(amount) FROM payments WHERE invoice_id = ?", 
                                     (data['invoice_id'],)).fetchone()[0] or 0
            
            if total_paid >= invoice['total']:
                conn.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", 
                           (data['invoice_id'],))
            elif total_paid > 0:
                conn.execute("UPDATE invoices SET status = 'partially_paid' WHERE id = ?", 
                           (data['invoice_id'],))
            
            conn.commit()
        
        return jsonify({'success': True, 'data': {'id': payment_id}}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------- REPORTING ENDPOINTS ----------

@app.route('/api/v1/reports/summary', methods=['GET'])
@require_api_key
def get_summary():
    """Get financial summary"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        with get_db_connection() as conn:
            # Revenue
            revenue_query = "SELECT SUM(total) as total FROM invoices WHERE status = 'paid'"
            params = []
            
            if start_date and end_date:
                revenue_query += " AND date BETWEEN ? AND ?"
                params = [start_date, end_date]
            
            revenue = conn.execute(revenue_query, tuple(params)).fetchone()['total'] or 0
            
            # Expenses
            expense_query = "SELECT SUM(amount) as total FROM expenses WHERE 1=1"
            exp_params = []
            
            if start_date and end_date:
                expense_query += " AND date BETWEEN ? AND ?"
                exp_params = [start_date, end_date]
            
            expenses = conn.execute(expense_query, tuple(exp_params)).fetchone()['total'] or 0
            
            # Outstanding
            outstanding = conn.execute(
                "SELECT SUM(total) as total FROM invoices WHERE status = 'unpaid'"
            ).fetchone()['total'] or 0
        
        return jsonify({
            'success': True,
            'data': {
                'revenue': revenue,
                'expenses': expenses,
                'profit': revenue - expenses,
                'outstanding': outstanding
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------- UTILITY ENDPOINTS ----------

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/api/v1/tax/calculate', methods=['POST'])
@require_api_key
def calculate_tax():
    """Calculate tax on an amount"""
    try:
        data = request.get_json()
        
        if 'amount' not in data or 'tax_rate' not in data:
            return jsonify({'success': False, 'error': 'Missing amount or tax_rate'}), 400
        
        result = TaxCalculator.calculate_tax(
            data['amount'], 
            data['tax_rate'], 
            data.get('tax_type', 'VAT')
        )
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/currency/convert', methods=['POST'])
@require_api_key
def convert_currency():
    """Convert currency"""
    try:
        data = request.get_json()
        required_fields = ['amount', 'from_currency', 'to_currency']
        
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        converted = CurrencyConverter.convert(
            data['amount'],
            data['from_currency'],
            data['to_currency']
        )
        
        return jsonify({
            'success': True,
            'data': {
                'original_amount': data['amount'],
                'from_currency': data['from_currency'],
                'to_currency': data['to_currency'],
                'converted_amount': converted
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------- API KEY MANAGEMENT ----------

@app.route('/api/v1/api-keys', methods=['POST'])
def create_api_key():
    """Create a new API key (requires admin credentials)"""
    try:
        auth = request.authorization
        
        if not auth or not auth.username or not auth.password:
            return jsonify({'success': False, 'error': 'Admin credentials required'}), 401
        
        # Verify admin user
        with get_db_connection() as conn:
            from app import verify_password
            user = conn.execute("SELECT * FROM users WHERE username = ?", 
                              (auth.username,)).fetchone()
            
            if not user or not verify_password(user['password'], auth.password):
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
            # Generate API key
            import secrets
            api_key = secrets.token_urlsafe(32)
            created_at = datetime.datetime.now().isoformat()
            
            data = request.get_json() or {}
            description = data.get('description', 'API Key')
            
            conn.execute(
                """INSERT INTO api_keys (key, description, is_active, created_at, created_by) 
                   VALUES (?, ?, ?, ?, ?)""",
                (api_key, description, 1, created_at, auth.username)
            )
            conn.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'api_key': api_key,
                'description': description,
                'created_at': created_at
            }
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------- ERROR HANDLERS ----------

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ---------- RUN SERVER ----------

if __name__ == '__main__':
    # Run in development mode
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', 'False').lower() == 'true')
