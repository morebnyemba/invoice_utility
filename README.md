# Invoice Utility - Professional Business Management System

A comprehensive, production-ready invoice and business management system built with Python and Streamlit. **Works 100% offline** - designed for small to medium businesses with enterprise-grade features.

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

See `FIRST_TIME_SETUP.md` for detailed setup guide.

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

### 📊 Reporting & Analytics
- 💵 Revenue and expense tracking
- 📉 Profit margin analysis
- 👥 Client lifetime value (LTV)
- 🎯 Project profitability reports
- 📅 Invoice aging analysis
- 📈 Monthly performance charts
- 💾 Data export (CSV)
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

## 📋 Requirements

```
streamlit>=1.28.0
pandas>=1.5.0
reportlab>=3.6.0
plotly>=5.0.0
bcrypt>=4.0.0
psycopg2-binary>=2.9.0      # For PostgreSQL
mysql-connector-python>=8.0.0  # For MySQL
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
├── app.py                  # Main Streamlit application
├── database.py             # Database abstraction layer
├── db_schema.py            # Schema initialization and migrations
├── business_logic.py       # Business features and logic
├── requirements.txt        # Python dependencies
├── DATABASE_SETUP.md       # Database configuration guide
└── README.md              # This file
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

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 📧 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check the documentation
- Review the DATABASE_SETUP.md guide

## 🙏 Credits

Developed for Slyker Tech Web Services by Moreblessing Nyemba.

## 🔮 Roadmap

- [ ] REST API for integrations
- [ ] Mobile responsive design improvements
- [ ] Bulk invoice operations
- [ ] Advanced reporting dashboards
- [ ] Integration with payment gateways
- [ ] Multi-language support
- [ ] Invoice customization templates
- [ ] Client portal access
- [ ] Automated invoice generation from recurring schedules
- [ ] SMS notifications

---

**Version**: 2.0.0 (Enterprise Edition)  
**Last Updated**: January 2026
