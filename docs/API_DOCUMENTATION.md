# REST API Documentation

## Overview

The Invoice Utility provides a comprehensive REST API for integration with external systems, ERP software, accounting platforms, and custom applications.

**Base URL:** `http://localhost:5000/api/v1`

## Authentication

All API endpoints (except `/health`) require an API key for authentication.

### Getting an API Key

**Endpoint:** `POST /api/v1/api-keys`

**Authentication:** HTTP Basic Auth (admin username/password)

**Request:**
```bash
curl -X POST http://localhost:5000/api/v1/api-keys \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{"description": "ERP Integration Key"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "api_key": "your-generated-api-key",
    "description": "ERP Integration Key",
    "created_at": "2026-01-18T12:00:00"
  }
}
```

### Using API Key

Include the API key in the `X-API-Key` header for all requests:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/v1/clients
```

## Endpoints

### Health Check

**GET** `/api/v1/health`

Check API status (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2026-01-18T12:00:00"
}
```

---

## Clients

### List All Clients

**GET** `/api/v1/clients`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "CLIENT01",
      "name": "Acme Corp",
      "email": "contact@acme.com",
      "phone": "+1234567890",
      "created_at": "2026-01-01T00:00:00"
    }
  ],
  "count": 1
}
```

### Get Single Client

**GET** `/api/v1/clients/{client_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "CLIENT01",
    "name": "Acme Corp",
    "email": "contact@acme.com",
    "phone": "+1234567890",
    "created_at": "2026-01-01T00:00:00"
  }
}
```

### Create Client

**POST** `/api/v1/clients`

**Request Body:**
```json
{
  "name": "New Client Corp",
  "email": "client@example.com",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "ABC12345"
  }
}
```

---

## Invoices

### List All Invoices

**GET** `/api/v1/invoices`

**Query Parameters:**
- `status` (optional): Filter by status (`paid`, `unpaid`, `partially_paid`)
- `client_id` (optional): Filter by client ID

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:5000/api/v1/invoices?status=unpaid"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "ST-ABC123",
      "client_id": "CLIENT01",
      "client_name": "Acme Corp",
      "client_email": "contact@acme.com",
      "services": "[('Web Development', 1000.0)]",
      "total": 1000.0,
      "date": "15 January 2026",
      "status": "unpaid",
      "created_at": "2026-01-15T10:00:00"
    }
  ],
  "count": 1
}
```

### Get Single Invoice

**GET** `/api/v1/invoices/{invoice_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "ST-ABC123",
    "client_id": "CLIENT01",
    "client_name": "Acme Corp",
    "client_email": "contact@acme.com",
    "client_phone": "+1234567890",
    "services": "[('Web Development', 1000.0)]",
    "total": 1000.0,
    "date": "15 January 2026",
    "status": "unpaid",
    "created_at": "2026-01-15T10:00:00"
  }
}
```

### Create Invoice

**POST** `/api/v1/invoices`

**Request Body:**
```json
{
  "client_id": "CLIENT01",
  "services": [["Web Development", 1000.0], ["Hosting", 100.0]],
  "total": 1100.0,
  "date": "18 January 2026",
  "status": "unpaid",
  "project_id": "PROJ001"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "ST-DEF456"
  }
}
```

### Download Invoice PDF

**GET** `/api/v1/invoices/{invoice_id}/pdf`

Downloads the invoice as a PDF file.

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  -O -J http://localhost:5000/api/v1/invoices/ST-ABC123/pdf
```

---

## Payments

### Record Payment

**POST** `/api/v1/payments`

**Request Body:**
```json
{
  "invoice_id": "ST-ABC123",
  "amount": 500.0,
  "date": "2026-01-18",
  "method": "Bank Transfer",
  "notes": "Partial payment received"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "PAY12345"
  }
}
```

**Note:** Invoice status is automatically updated based on total payments received.

---

## Reports

### Financial Summary

**GET** `/api/v1/reports/summary`

**Query Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:5000/api/v1/reports/summary?start_date=2026-01-01&end_date=2026-01-31"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "revenue": 15000.0,
    "expenses": 5000.0,
    "profit": 10000.0,
    "outstanding": 3000.0
  }
}
```

---

## Utilities

### Calculate Tax

**POST** `/api/v1/tax/calculate`

**Request Body:**
```json
{
  "amount": 1000.0,
  "tax_rate": 15.0,
  "tax_type": "VAT"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subtotal": 1000.0,
    "tax_type": "VAT",
    "tax_rate": 15.0,
    "tax_amount": 150.0,
    "total": 1150.0
  }
}
```

### Convert Currency

**POST** `/api/v1/currency/convert`

**Request Body:**
```json
{
  "amount": 1000.0,
  "from_currency": "USD",
  "to_currency": "EUR"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "original_amount": 1000.0,
    "from_currency": "USD",
    "to_currency": "EUR",
    "converted_amount": 850.0
  }
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (missing/invalid parameters)
- `401` - Unauthorized (invalid/missing API key)
- `404` - Not Found
- `500` - Internal Server Error

---

## Running the API Server

### Development Mode

```bash
# Start the API server
python api.py

# Or with custom port
python -c "from api import app; app.run(host='0.0.0.0', port=5000)"
```

### Production Mode

Use a production WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

### Environment Variables

```bash
# API Configuration
export API_SECRET_KEY=your-secret-key-here
export DEBUG=false

# Database Configuration (uses same as main app)
export DB_TYPE=postgresql
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=invoice_user
export DB_PASSWORD=your_password
export DB_DATABASE=invoice_db
```

---

## Integration Examples

### Python

```python
import requests

API_KEY = "your-api-key"
BASE_URL = "http://localhost:5000/api/v1"

headers = {"X-API-Key": API_KEY}

# Get all clients
response = requests.get(f"{BASE_URL}/clients", headers=headers)
clients = response.json()['data']

# Create invoice
invoice_data = {
    "client_id": "CLIENT01",
    "services": [["Consulting", 2000.0]],
    "total": 2000.0,
    "date": "18 January 2026"
}
response = requests.post(f"{BASE_URL}/invoices", json=invoice_data, headers=headers)
invoice_id = response.json()['data']['id']

# Record payment
payment_data = {
    "invoice_id": invoice_id,
    "amount": 2000.0,
    "date": "2026-01-20",
    "method": "Wire Transfer"
}
requests.post(f"{BASE_URL}/payments", json=payment_data, headers=headers)
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const API_KEY = 'your-api-key';
const BASE_URL = 'http://localhost:5000/api/v1';

const headers = { 'X-API-Key': API_KEY };

// Get all invoices
async function getInvoices() {
  const response = await axios.get(`${BASE_URL}/invoices`, { headers });
  return response.data.data;
}

// Create client
async function createClient(name, email, phone) {
  const response = await axios.post(
    `${BASE_URL}/clients`,
    { name, email, phone },
    { headers }
  );
  return response.data.data.id;
}
```

### cURL

```bash
# Set API key
API_KEY="your-api-key"

# Get financial summary
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:5000/api/v1/reports/summary"

# Create invoice
curl -X POST \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "CLIENT01",
    "services": [["Web Development", 3000.0]],
    "total": 3000.0,
    "date": "18 January 2026"
  }' \
  http://localhost:5000/api/v1/invoices
```

---

## Security Best Practices

1. **Use HTTPS in production** - Never send API keys over unencrypted connections
2. **Rotate API keys regularly** - Generate new keys and revoke old ones
3. **Limit API key permissions** - Use different keys for different integrations
4. **Monitor API usage** - Track which keys are being used and when
5. **Set rate limits** - Implement rate limiting in production
6. **Validate input** - Always validate and sanitize input data
7. **Use environment variables** - Never hardcode API keys or secrets

---

## Rate Limiting (Production)

For production deployments, implement rate limiting:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/v1/invoices')
@limiter.limit("10 per minute")
@require_api_key
def get_invoices():
    # ... endpoint code
```

---

## Webhooks (Future Enhancement)

Future versions will support webhooks for real-time notifications:
- Invoice created
- Payment received
- Invoice overdue
- Client updated

---

## Support

For API support and questions:
- Check the main README.md
- Review integration examples above
- Test endpoints with the health check first
- Verify API key is correct and active

---

**API Version:** 1.0  
**Last Updated:** January 2026
