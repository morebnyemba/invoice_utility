# Quick Start Guide

## Getting Started in 5 Minutes

### Option 1: Basic Setup (SQLite - No Configuration Needed)

```bash
# 1. Clone the repository
git clone https://github.com/morebnyemba/invoice_utility.git
cd invoice_utility

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run app.py

# 4. Open your browser to the URL shown (usually http://localhost:8501)

# 5. Create your admin account on first run
```

That's it! You're ready to create invoices.

### Option 2: Production Setup (PostgreSQL)

```bash
# 1. Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# 2. Create database and user
sudo -u postgres psql
CREATE DATABASE invoice_db;
CREATE USER invoice_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE invoice_db TO invoice_user;
\q

# 3. Clone and install
git clone https://github.com/morebnyemba/invoice_utility.git
cd invoice_utility
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with your database settings

# Example configuration:
# DB_TYPE=postgresql
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=invoice_user
# DB_PASSWORD=your_secure_password
# DB_DATABASE=invoice_db

# 5. Run the application
streamlit run app.py
```

## First-Time Setup

### 1. Create Admin Account
- Open the application in your browser
- Fill in username and password
- Password must be at least 8 characters with uppercase, lowercase, and numbers
- Click "Sign Up"

### 2. Configure Company Settings
- Go to Settings → Company & Invoice
- Enter your company name, address, phone, email
- Set up payment details
- Save settings

### 3. Configure Tax (Optional)
- Go to Settings → Tax & Currency
- Enable tax calculation if needed
- Select tax type (VAT/GST/Sales Tax)
- Set tax rate
- Enter tax registration number

### 4. Configure Email (Optional)
- Go to Settings → Email (SMTP)
- Enter SMTP server details
- Set SMTP password as environment variable: `export SMTP_PASSWORD=your_password`
- Configure email templates
- Save settings

## Common Tasks

### Creating Your First Invoice

1. **Add a Client**
   - Go to "👥 Manage Clients"
   - Click "Add New Client"
   - Enter client name, email, phone
   - Save

2. **Create Invoice**
   - Go to "📝 Create Invoice"
   - Select your client
   - Add services and prices
   - Click "Generate Invoice"
   - Download PDF

### Recording a Payment

1. Go to "📊 Invoice Management"
2. Find the invoice
3. Click "💰 Record Payment"
4. Enter amount, date, and method
5. Save - invoice status updates automatically

### Creating a Project

1. Go to "🛠️ Project Management"
2. Fill in project details
3. Assign to client
4. Set budget and status
5. Save
6. Link invoices to this project

### Viewing Reports

1. Go to "📄 Reports"
2. Select date range
3. View financial, project, or client reports
4. Download CSV for further analysis

## Tips & Tricks

### Performance
- Use PostgreSQL or MySQL for more than 100 invoices/month
- Enable connection pooling in production
- Regular database backups

### Security
- Change default SECRET_KEY in production
- Use strong passwords
- Set appropriate session timeout
- Enable HTTPS in production
- Keep database credentials in .env file (never commit)

### Backup
- Go to Settings → Database & Security
- Click "Create Database Backup"
- Download the backup file
- Store securely off-site

### Multi-User
- Create users with different roles
- Admin: Full access
- Manager: Can't change settings
- Accountant: Focus on financials
- Viewer: Read-only access

## Troubleshooting

### Can't connect to database
```bash
# Check database is running
systemctl status postgresql  # or mysql

# Verify credentials in .env file
cat .env

# Test connection
psql -h localhost -U invoice_user -d invoice_db
```

### Module not found error
```bash
# Install all dependencies
pip install -r requirements.txt

# For PostgreSQL support
pip install psycopg2-binary

# For MySQL support
pip install mysql-connector-python
```

### Session timeout issues
```bash
# Increase session timeout (in seconds)
export SESSION_TIMEOUT=7200  # 2 hours
```

### Email not sending
- Verify SMTP settings in Settings → Email
- Check SMTP_PASSWORD environment variable
- Test with a simple email client first
- Check firewall rules

## Testing Your Setup

Run the system test:
```bash
python3 test_system.py
```

All tests should pass:
- ✓ Module Imports: PASS
- ✓ Database Connection: PASS
- ✓ Business Logic: PASS

## Getting Help

1. Check the README.md for detailed documentation
2. Review DATABASE_SETUP.md for database configuration
3. Read ENHANCEMENTS.md for feature details
4. Check application logs for errors
5. Open an issue on GitHub

## Next Steps

After basic setup:
1. ✓ Create admin account
2. ✓ Configure company settings
3. ✓ Add your first client
4. ✓ Create your first invoice
5. ⭐ Explore advanced features:
   - Set up recurring invoices for subscriptions
   - Configure tax calculation
   - Create invoice templates
   - Set up projects
   - Track expenses
   - Generate reports
   - Configure multi-user access

## Production Deployment

For production deployment:
1. Use PostgreSQL or MySQL
2. Set up HTTPS/SSL
3. Configure firewall
4. Enable automated backups
5. Set up monitoring
6. Use environment variables for all secrets
7. Regular security updates

Refer to README.md for complete production checklist.

---

**Need More Help?** 
- 📚 Full Documentation: README.md
- 🗄️ Database Setup: DATABASE_SETUP.md  
- ✨ New Features: ENHANCEMENTS.md
- 🧪 Run Tests: `python3 test_system.py`
