# Invoice Utility - Professional Business Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-brightgreen.svg)](https://github.com/morebnyemba/invoice_utility)
[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](CHANGELOG.md)

A comprehensive, production-ready invoice and business management system built with Python and Streamlit. **Works 100% offline** - designed for small to medium businesses with enterprise-grade features.

## 🎉 What's New in v2.1.0

- 📦 **Bulk Operations** - Create, update, or delete multiple invoices at once
- 📊 **Advanced Analytics** - Revenue forecasting and predictive insights
- 🤖 **Automated Scheduler** - Automatic recurring invoice generation
- 📁 **Organized Code** - Clean folder structure for better maintainability

See [CHANGELOG.md](CHANGELOG.md) for full details and [docs/NEW_FEATURES.md](docs/NEW_FEATURES.md) for documentation.

## 📜 Open Source & License

This is **free and open source software** released under the [MIT License](LICENSE).

**You are free to:**
- ✅ Use commercially
- ✅ Modify for your needs
- ✅ Distribute copies
- ✅ Use privately
- ✅ Integrate with other systems

**Only requirement:** Attribution - Include credit to the original author (Moreblessing Nyemba) and a link to this repository.

## 🔌 REST API Support

**NEW:** Full REST API for integration with external systems, ERP software, and custom applications.

- ✅ Complete HTTP endpoints for all operations
- ✅ JSON request/response format
- ✅ API key authentication
- ✅ Comprehensive documentation
- ✅ Ready for ERP/accounting system integration
- ✅ Support for automated workflows

See [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for complete API reference.

## ✈️ Offline-First Design

**This application works completely without internet connection:**
- ✅ All core features available offline
- ✅ Data stored locally on your device
- ✅ No external dependencies for core operations
- ✅ Privacy-focused - no data sent anywhere
- ⚠️ Email sending is the only feature that requires internet (optional)

## 🎯 Quick Setup (5 minutes)

1. **Install and run:**
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

2. **Configure YOUR business details:**
   - Create admin account
   - Go to Settings → Company & Invoice
   - Replace default placeholders with your information
   - Start invoicing!

See [docs/FIRST_TIME_SETUP.md](docs/FIRST_TIME_SETUP.md) for detailed setup guide.

## 🚀 Key Features

### Core Invoice Management
- ✅ Create and manage professional invoices
- ✅ PDF generation with company branding
- ✅ Client and project management
- ✅ Payment tracking and history
- ✅ Invoice status management (Paid/Unpaid/Partially Paid)
- ✅ Secure invoice sharing links

### 💼 Business Logic Features
- 📋 **Invoice Templates** - Save frequently used service combinations
- 🔄 **Recurring Invoices** - Automated subscription billing (weekly/monthly/quarterly/yearly)
- 💰 **Tax Calculation** - VAT/GST/Sales Tax support with configurable rates
- 🌍 **Multi-Currency Support** - Handle international invoicing
- 📊 **Advanced Analytics** - Profit margins, client lifetime value, project profitability
- 📧 **Email Integration** - Send invoices directly to clients
- 🔔 **Invoice Reminders** - Track and send overdue payment reminders
- 📈 **Expense Tracking** - Monitor business expenses by category
- 🎯 **Project Management** - Link invoices to projects, track budgets

### 🔒 Security & Access Control
- 🔐 Role-based access control (Admin/Manager/Accountant/Viewer)
- 🔑 Secure password hashing with bcrypt
- 📝 Audit logging for all business actions
- ⏱️ Session timeout management
- 🛡️ Input validation and sanitization

### 🗄️ Database Support
- **SQLite** - Default, no setup required
- **PostgreSQL** - Enterprise-grade relational database
- **MySQL** - Popular open-source database
- Connection pooling for better performance
- Automatic schema migrations

### 🔌 API & Integration
- **REST API** - Full HTTP API for external integrations
- **JSON Format** - Standard request/response format
- **API Authentication** - Secure API key-based auth
- **ERP Integration** - Connect with accounting systems
- **Custom Integrations** - Build your own tools on top
- See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for details

### 📊 Reporting & Analytics
- 💵 Revenue and expense tracking
- 📉 Profit margin analysis
- 👥 Client lifetime value (LTV)
- 🎯 Project profitability reports
- 📅 Invoice aging analysis
- 📈 Monthly performance charts
- 💾 Data export (CSV)
- 🔄 Database backup and restore

### 🆕 Advanced Features (NEW!)
- 📦 **Bulk Operations** - Create, update, or delete multiple invoices at once
- 📊 **Advanced Reporting** - Revenue trends, predictive analytics, expense breakdowns
- 🤖 **Automated Scheduler** - Automatic recurring invoice generation
- 📧 **Notification System** - Automated email notifications for generated invoices
- 📈 **Predictive Analytics** - Revenue forecasting based on historical data
- 📉 **Client Performance Metrics** - Detailed client analysis and lifetime value
- 🎯 **Project Profitability** - In-depth project profitability analysis
- ⏰ **Invoice Aging Reports** - Track overdue invoices by age brackets
- 🔄 Database backup and restore

## 🛠️ Installation

### Quick Start (SQLite)

```bash
# Clone the repository
git clone https://github.com/morebnyemba/invoice_utility.git
cd invoice_utility

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Production Setup (PostgreSQL/MySQL)

See [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed database configuration.

### API Server Setup

```bash
# Start the REST API server (in addition to Streamlit app)
python run_api.py

# Or with Gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.api.api:app
```

See [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for complete API reference.

## 📋 Requirements

```
streamlit>=1.28.0
pandas>=1.5.0
reportlab>=3.6.0
plotly>=5.0.0
bcrypt>=4.0.0
psycopg2-binary>=2.9.0          # For PostgreSQL
mysql-connector-python>=8.0.0    # For MySQL
flask>=2.3.0                     # For REST API
pyjwt>=2.8.0                     # For API authentication
```

## ⚙️ Configuration

### Environment Variables

```bash
# Database Configuration
DB_TYPE=sqlite              # sqlite, postgresql, or mysql
DB_NAME=invoices.db         # For SQLite
DB_HOST=localhost           # For PostgreSQL/MySQL
DB_PORT=5432               # 5432 for PostgreSQL, 3306 for MySQL
DB_USER=your_user
DB_PASSWORD=your_password
DB_DATABASE=invoice_db

# Connection Pool (PostgreSQL/MySQL)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Application Settings
SECRET_KEY=your-secret-key-here
SESSION_TIMEOUT=3600        # Session timeout in seconds (1 hour)
DEBUG=false

# SMTP Configuration (for email features)
SMTP_PASSWORD=your_smtp_password

# Optional
LOGO_PATH=logo.png
```

### First Time Setup

1. Run the application: `streamlit run app.py`
2. Create your admin account
3. Configure company settings in Settings → Company & Invoice
4. Configure tax settings (if applicable)
5. Set up SMTP for email features (optional)

## 📖 Usage Guide

### Creating Invoices

1. Navigate to "📝 Create Invoice"
2. Select existing client or create new
3. Add services and prices
4. Link to project (optional)
5. Generate and download PDF

### Managing Clients

1. Go to "👥 Manage Clients"
2. Add client details (name, email, phone)
3. Edit or delete as needed
4. View client invoice history

### Project Management

1. Navigate to "🛠️ Project Management"
2. Create projects linked to clients
3. Set budgets and track status
4. Link invoices to projects
5. Monitor project profitability

### Recording Payments

1. Go to "📊 Invoice Management"
2. Find the invoice
3. Click "💰 Record Payment"
4. Enter amount, date, and payment method
5. Invoice status updates automatically

### Tax Configuration

1. Settings → Tax & Currency
2. Enable tax calculation
3. Select tax type (VAT/GST/Sales Tax)
4. Set tax rate percentage
5. Enter tax registration number

### Recurring Invoices

Recurring invoices automatically generate based on schedule:
- Weekly
- Monthly
- Quarterly
- Yearly

Configure in the application for subscription-based billing.

## 🏗️ Architecture

### Module Structure

```
invoice_utility/
├── app.py                      # Main Streamlit application entry point
├── run_api.py                  # REST API server entry point
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
├── README.md                   # This file
├── .env.example                # Configuration template
├── .gitignore                  # Git ignore rules
├── src/                        # Source code directory
│   ├── __init__.py
│   ├── models/                 # Database layer
│   │   ├── __init__.py
│   │   ├── database.py         # Database abstraction layer
│   │   └── db_schema.py        # Schema initialization and migrations
│   ├── business/               # Business logic layer
│   │   ├── __init__.py
│   │   └── business_logic.py   # Business features and logic
│   ├── api/                    # REST API layer
│   │   ├── __init__.py
│   │   └── api.py              # Flask API endpoints
│   └── utils/                  # Utility functions
│       └── __init__.py
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_system.py          # System integration tests
└── docs/                       # Documentation
    ├── README.md               # Detailed README
    ├── API_DOCUMENTATION.md    # Complete API reference
    ├── DATABASE_SETUP.md       # Database configuration guide
    ├── QUICKSTART.md           # Quick start guide
    ├── FIRST_TIME_SETUP.md     # First-time configuration
    ├── OFFLINE_GUIDE.md        # Offline operation guide
    └── ENHANCEMENTS.md         # Enhancement details
```

### Database Schema

**Core Tables:**
- `users` - User accounts with role-based access
- `clients` - Client information
- `projects` - Project management
- `invoices` - Invoice records
- `payments` - Payment tracking
- `expenses` - Business expenses
- `settings` - Application configuration

**Business Feature Tables:**
- `invoice_templates` - Reusable invoice templates
- `recurring_invoices` - Subscription billing schedules
- `audit_logs` - Activity tracking
- `invoice_reminders` - Payment reminder history
- `api_keys` - API authentication tokens

## 🔐 Security Features

- **Password Hashing**: bcrypt with salt
- **Input Sanitization**: Protection against XSS and SQL injection
- **Email Validation**: RFC-compliant email checking
- **Session Management**: Configurable timeout
- **Role-Based Access**: Fine-grained permissions
- **Audit Trail**: Complete action logging
- **Secure Sharing**: Token-based invoice links with expiry

## 📊 Business Intelligence

### Key Metrics
- Total Revenue
- Total Expenses
- Net Profit
- Outstanding Invoices
- Profit Margin
- Client Lifetime Value
- Project Profitability

### Visual Analytics
- Monthly revenue vs expenses
- Expense breakdown by category
- Invoice aging analysis
- Client revenue comparison
- Project performance charts

## 🚀 Production Deployment

### Recommended Stack

- **Application**: Streamlit
- **Database**: PostgreSQL (recommended) or MySQL
- **Web Server**: Nginx (reverse proxy)
- **Process Manager**: Supervisor or systemd
- **SSL**: Let's Encrypt

### Deployment Checklist

- [ ] Configure PostgreSQL/MySQL database
- [ ] Set all environment variables
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Enable monitoring and logging
- [ ] Test email functionality
- [ ] Configure session timeout
- [ ] Review security settings
- [ ] Set up regular database maintenance

## 🔧 Maintenance

### Regular Tasks

- **Daily**: Monitor invoice generation
- **Weekly**: Review outstanding payments
- **Monthly**: Generate financial reports, backup database
- **Quarterly**: Review tax settings, update exchange rates
- **Yearly**: Audit security settings, update dependencies

### Backup Strategy

1. Use built-in database backup feature
2. Store backups in secure location
3. Test restore procedures regularly
4. Keep at least 30 days of backups

## 📈 Scaling Considerations

### Performance Optimization

- Use PostgreSQL/MySQL for production
- Enable connection pooling
- Add database indexes for large datasets
- Implement caching for frequently accessed data
- Consider CDN for static assets

### Multi-User Support

- Role-based access control included
- Concurrent user support with proper database backend
- Session management per user
- Audit logging for accountability

## 🤝 Contributing

This is **open source software** and contributions are welcome!

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Contribution Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass
- Keep commits atomic and well-described

## 📝 License

**MIT License with Attribution Requirement**

Copyright (c) 2026 Moreblessing Nyemba

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for full details.

**TL;DR:** You can use this software for **any purpose** (personal, commercial, etc.), modify it, and distribute it. The only requirement is to **give credit** to the original author.

### Using This Software

When using this software:
- ✅ Include the LICENSE file in your distribution
- ✅ Credit the original author: Moreblessing Nyemba
- ✅ Link back to: https://github.com/morebnyemba/invoice_utility

**Example Attribution:**
```
Based on Invoice Utility by Moreblessing Nyemba
https://github.com/morebnyemba/invoice_utility
```

## 🔌 API Integration Examples

### ERP System Integration

```python
# Example: Sync invoices to external ERP
import requests

API_KEY = "your-api-key"
API_URL = "http://localhost:5000/api/v1"

# Get all unpaid invoices
response = requests.get(
    f"{API_URL}/invoices?status=unpaid",
    headers={"X-API-Key": API_KEY}
)

for invoice in response.json()['data']:
    # Send to external ERP system
    sync_to_erp(invoice)
```

### Automated Reporting

```python
# Example: Daily revenue report
from datetime import date, timedelta

today = date.today()
start_date = today - timedelta(days=30)

response = requests.get(
    f"{API_URL}/reports/summary",
    params={"start_date": start_date, "end_date": today},
    headers={"X-API-Key": API_KEY}
)

summary = response.json()['data']
send_email_report(summary)
```

### Third-Party Payment Gateway

```python
# Example: Record payment from payment gateway webhook
@app.route('/webhook/payment', methods=['POST'])
def payment_webhook():
    payment_data = request.json
    
    # Record in invoice system
    requests.post(
        f"{API_URL}/payments",
        json={
            "invoice_id": payment_data['invoice_id'],
            "amount": payment_data['amount'],
            "date": payment_data['date'],
            "method": payment_data['gateway']
        },
        headers={"X-API-Key": API_KEY}
    )
    
    return "OK", 200
```

## 📧 Support & Community

### Getting Help

- 📖 **Documentation**: Check README, QUICKSTART, and API_DOCUMENTATION
- 🐛 **Issues**: [Report bugs on GitHub](https://github.com/morebnyemba/invoice_utility/issues)
- 💡 **Feature Requests**: Open an issue with the "enhancement" label
- 🔧 **Configuration**: See docs/DATABASE_SETUP.md and docs/FIRST_TIME_SETUP.md

### 📚 Documentation

#### Getting Started
- [Quick Start Guide](docs/QUICKSTART.md) - Get started in 5 minutes
- [First-Time Setup](docs/FIRST_TIME_SETUP.md) - Initial configuration guide
- [Migration Guide](docs/MIGRATION_GUIDE.md) - Upgrade from older versions

#### Features & Usage
- [NEW FEATURES](docs/NEW_FEATURES.md) - Complete guide to v2.1.0 features ⭐
- [API Documentation](docs/API_DOCUMENTATION.md) - Complete REST API reference
- [Database Setup](docs/DATABASE_SETUP.md) - PostgreSQL/MySQL configuration
- [Offline Guide](docs/OFFLINE_GUIDE.md) - Offline operation details

#### Technical Documentation
- [CHANGELOG](CHANGELOG.md) - Version history and changes
- [Enhancements](docs/ENHANCEMENTS.md) - Technical enhancement details
- [Architecture](docs/README.md) - Detailed architecture documentation

## 🙏 Credits & Acknowledgments

**Developed by:** [Moreblessing Nyemba](https://github.com/morebnyemba)

**Original Project:** Invoice Utility for Slyker Tech Web Services

**Contributors:** Open to community contributions

### Built With

- [Streamlit](https://streamlit.io/) - Web UI framework
- [Flask](https://flask.palletsprojects.com/) - REST API framework
- [ReportLab](https://www.reportlab.com/) - PDF generation
- [Plotly](https://plotly.com/) - Interactive charts
- [bcrypt](https://github.com/pyca/bcrypt/) - Password hashing

## 📊 Project Stats

- **Version:** 2.1.0
- **Language:** Python 3.8+
- **License:** MIT with Attribution
- **Type:** Open Source Business Software
- **Status:** Production Ready ✅
- **Maintenance:** Actively Maintained
- **Tests:** Passing ✅
- **Security:** No Known Vulnerabilities ✅

## 🔮 Roadmap

- [x] REST API for integrations ✅
- [x] Bulk invoice operations ✅
- [x] Advanced reporting dashboards ✅
- [x] Automated invoice generation from recurring schedules ✅
- [ ] Mobile responsive design improvements
- [ ] Integration with payment gateways
- [ ] Multi-language support
- [ ] Invoice customization templates (UI)
- [ ] Client portal access
- [ ] SMS notifications

---

**Version**: 2.0.0 (Enterprise Edition)  
**Last Updated**: January 2026
