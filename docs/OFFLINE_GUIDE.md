# Offline Operation Guide

## 🌐 Internet Connectivity Requirements

### ✅ Works 100% Offline (Core Features)

The following features work **without any internet connection**:

**Invoice Management:**
- Create invoices
- Edit invoices
- Delete invoices
- Generate PDF invoices
- View invoice history
- Record payments
- Track payment history

**Client Management:**
- Add/edit/delete clients
- View client information
- Track client history

**Project Management:**
- Create and manage projects
- Link invoices to projects
- Track project budgets
- Monitor project status

**Financial Operations:**
- Record expenses
- Track revenue
- Calculate profit margins
- Generate financial reports
- View analytics and charts

**Data Management:**
- Database operations (SQLite/PostgreSQL/MySQL - all work offline)
- Database backups
- Data export (CSV)
- Settings configuration

**Security:**
- User authentication
- Role-based access control
- Password management
- Session management
- Audit logging

### ⚠️ Requires Internet (Optional Features)

Only **one optional feature** requires internet:

**Email Sending:**
- Send invoices via email to clients
- Requires SMTP server connection
- **This is completely optional** - you can download PDFs and send them manually

**One-Time Setup (Requires Internet):**
- Installing Python packages (`pip install`)
- Downloading database drivers for PostgreSQL/MySQL (if using these databases)
- Cloning the repository (initial setup only)

## 💾 Data Storage

**All data is stored locally on your device:**
- SQLite database file (`invoices.db`) stored in application directory
- PostgreSQL/MySQL can be installed locally (no internet needed)
- No data sent to external servers
- Complete privacy and data ownership

## 🚀 Deployment Scenarios

### Scenario 1: Single Computer, No Internet
```bash
# One-time setup (with internet)
pip install -r requirements.txt

# From now on, works completely offline
streamlit run app.py
```
**Result:** Full functionality, all data local, no internet needed ever.

### Scenario 2: Local Network, Multiple Users
```bash
# Setup PostgreSQL locally (no internet)
# Configure DB_TYPE=postgresql with local host
# Multiple users can connect via LAN
```
**Result:** Multi-user system, no internet required.

### Scenario 3: Air-Gapped System
```bash
# Install on a computer with internet
pip install -r requirements.txt

# Copy entire folder to air-gapped computer
# No internet access needed
streamlit run app.py
```
**Result:** Works perfectly on isolated systems.

## 📦 What Gets Installed (One-Time)

**Core Dependencies (All work offline after installation):**
- `streamlit` - Web interface (works on localhost)
- `pandas` - Data processing
- `reportlab` - PDF generation
- `plotly` - Charts and graphs
- `bcrypt` - Password security
- `sqlite3` - Built into Python (no internet needed)

**Optional Dependencies (For specific database backends):**
- `psycopg2-binary` - PostgreSQL support (can be used locally)
- `mysql-connector-python` - MySQL support (can be used locally)

All these libraries work offline once installed.

## 🔒 Privacy & Security

**This application is completely private:**
- ❌ No telemetry or tracking
- ❌ No data sent to external servers
- ❌ No API calls to external services
- ❌ No cloud dependencies
- ✅ All data stays on your device
- ✅ You have complete control

## 🌍 Use Cases

**Perfect for:**
- Businesses in areas with unreliable internet
- Consultants who work on the go
- Organizations requiring data privacy
- Air-gapped or secure environments
- Anyone who values data ownership
- Offline-first workflows

**Not Limited by:**
- Internet outages
- Bandwidth constraints
- Data caps
- Network security policies
- Cloud service availability

## 📝 Configuration

**Business Details are Now Configurable:**
- No hardcoded business information
- Configure YOUR details in Settings → Company & Invoice
- Generic defaults that prompt you to customize
- Easy to set up for any business

**Initial Setup:**
1. Install dependencies (one-time, requires internet)
2. Run application (offline from now on)
3. Create admin account
4. Configure YOUR business details
5. Start using immediately

## 🆘 Troubleshooting

**"Module not found" error:**
- Solution: Run `pip install -r requirements.txt` (one-time, requires internet)
- After installation, everything works offline

**"Cannot connect to database":**
- SQLite: Always works offline (default)
- PostgreSQL/MySQL: Can be installed locally for offline use

**"Email not sending":**
- This is expected if offline
- Email is the only feature requiring internet
- Download PDFs and send manually instead

## ✨ Summary

**This invoice utility is designed for offline operation:**
- ✅ 99% of features work without internet
- ✅ Only email sending requires connectivity (optional)
- ✅ All data stored locally
- ✅ Complete privacy
- ✅ No external dependencies
- ✅ Perfect for offline environments

Once installed, you can:
- Disconnect from internet
- Work completely offline
- Generate professional invoices
- Manage your entire business
- Keep all your data private

**Your data, your device, your control.** 🔒
