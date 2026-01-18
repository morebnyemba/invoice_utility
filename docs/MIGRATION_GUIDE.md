# Migration Guide - Version 2.1.0

## Overview

Version 2.1.0 introduces a new organized folder structure and several advanced features. This guide helps you migrate from the previous flat structure to the new organized structure.

---

## 🚀 Quick Migration (For Most Users)

If you're using the application with the default SQLite database:

### Step 1: Pull the Latest Changes
```bash
git pull origin main
```

### Step 2: No Database Migration Needed!
Your existing `invoices.db` file will continue to work. The new features use the existing schema with no breaking changes.

### Step 3: Run the Application
```bash
# Streamlit app (same as before)
streamlit run app.py

# API server (new command)
python run_api.py
```

That's it! You're ready to use the new features.

---

## 📂 What Changed?

### New Folder Structure

**Before (v2.0.0):**
```
invoice_utility/
├── app.py
├── api.py
├── database.py
├── db_schema.py
├── business_logic.py
├── test_system.py
├── README.md
└── ...
```

**After (v2.1.0):**
```
invoice_utility/
├── app.py                    # Main entry point (unchanged)
├── run_api.py                # New API entry point
├── src/
│   ├── models/               # Database layer
│   │   ├── database.py
│   │   └── db_schema.py
│   ├── business/             # Business logic
│   │   ├── business_logic.py
│   │   ├── bulk_operations.py      # NEW
│   │   ├── advanced_reporting.py   # NEW
│   │   └── scheduler.py            # NEW
│   ├── api/                  # REST API
│   │   └── api.py
│   └── utils/                # Utilities
├── tests/                    # Test suite
│   ├── test_system.py
│   └── test_new_features.py  # NEW
└── docs/                     # Documentation
    ├── README.md
    ├── NEW_FEATURES.md       # NEW
    └── ...
```

### Import Changes

**Before:**
```python
from database import get_db_connection
from business_logic import TaxCalculator
```

**After:**
```python
from src.models.database import get_db_connection
from src.business.business_logic import TaxCalculator
```

---

## 🔧 For Developers and Custom Integrations

If you have custom scripts or integrations that import from the old structure:

### Update Your Imports

1. **Database imports:**
```python
# Old
from database import get_db_connection, get_db_type

# New
from src.models.database import get_db_connection, get_db_type
```

2. **Business logic imports:**
```python
# Old
from business_logic import TaxCalculator, InvoiceTemplate

# New
from src.business.business_logic import TaxCalculator, InvoiceTemplate
```

3. **API imports:**
```python
# Old
from api import app

# New
from src.api.api import app
```

### Update Custom Scripts

Add this at the top of your custom scripts:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

---

## 🆕 New Features Available

After migrating, you can use these new features:

### 1. Bulk Operations
```python
from src.business.bulk_operations import BulkInvoiceOperations

# Create multiple invoices at once
invoice_data = [...]
result = BulkInvoiceOperations.bulk_create_invoices(conn, invoice_data)
```

### 2. Advanced Reporting
```python
from src.business.advanced_reporting import AdvancedReporting

# Get revenue trends
trends = AdvancedReporting.revenue_trend_analysis(conn, months=12)

# Get predictive analytics
predictions = AdvancedReporting.predictive_analytics(conn)
```

### 3. Automated Scheduler
```python
from src.business.scheduler import InvoiceScheduler

# Start automatic recurring invoice generation
scheduler = InvoiceScheduler(get_db_connection)
scheduler.start()
```

See [NEW_FEATURES.md](NEW_FEATURES.md) for complete documentation.

---

## 🐛 Troubleshooting

### Problem: ImportError after update

**Error:**
```
ImportError: No module named 'database'
```

**Solution:**
Update your imports to use the new structure:
```python
from src.models.database import get_db_connection
```

### Problem: API server won't start

**Error:**
```
python: can't open file 'api.py'
```

**Solution:**
Use the new entry point:
```bash
python run_api.py
```

Or run directly:
```bash
python -m src.api.api
```

### Problem: Tests failing

**Solution:**
Run tests from the project root:
```bash
python tests/test_system.py
python tests/test_new_features.py
```

### Problem: Streamlit app won't start

**Solution:**
Make sure you're running from the project root:
```bash
cd /path/to/invoice_utility
streamlit run app.py
```

---

## 📦 For Docker Users

If you're using Docker, update your Dockerfile:

**Before:**
```dockerfile
CMD ["streamlit", "run", "app.py"]
```

**After:**
```dockerfile
# No change needed for Streamlit
CMD ["streamlit", "run", "app.py"]

# For API server
CMD ["python", "run_api.py"]
```

---

## 🔄 For CI/CD Pipelines

Update your CI/CD scripts:

**Before:**
```bash
python test_system.py
```

**After:**
```bash
python tests/test_system.py
python tests/test_new_features.py
```

---

## 📊 Database Compatibility

### No Migration Required ✅

- Existing SQLite databases work without modification
- All existing tables and data remain compatible
- New features use existing schema
- Automatic schema updates on first run

### New Tables (Created Automatically)

If you don't have these tables, they'll be created automatically:
- `recurring_invoices` - For recurring invoice schedules
- `audit_logs` - For tracking actions and notifications
- `expenses` - For expense tracking
- `projects` - For project management

---

## 🎯 Deployment Changes

### Production Deployment

**Streamlit App:**
```bash
# No change
streamlit run app.py --server.port 8501
```

**API Server:**
```bash
# Old
gunicorn -w 4 -b 0.0.0.0:5000 api:app

# New
gunicorn -w 4 -b 0.0.0.0:5000 src.api.api:app
```

### Systemd Service Files

Update your systemd service file:

**Before:**
```ini
[Service]
ExecStart=/usr/bin/python3 api.py
```

**After:**
```ini
[Service]
ExecStart=/usr/bin/python3 run_api.py
```

---

## 🔐 Security Notes

### No New Security Concerns

- All security features maintained
- Password hashing unchanged
- Session management unchanged
- API authentication unchanged

### New Audit Logging

The scheduler and notification systems now log to `audit_logs` table:
- Track when invoices are auto-generated
- Track when notifications are sent
- Useful for compliance and debugging

---

## 📈 Performance Impact

### Minimal Impact

- No performance degradation from restructuring
- Same database queries
- Same response times
- Improved code maintainability

### New Features Performance

- **Bulk operations:** More efficient than individual operations
- **Reporting:** May take longer for large datasets (>10,000 records)
- **Scheduler:** Minimal background resource usage

---

## ✅ Verification Checklist

After migration, verify everything works:

- [ ] Streamlit app starts: `streamlit run app.py`
- [ ] Can view existing invoices
- [ ] Can create new invoices
- [ ] Can view clients and projects
- [ ] API server starts: `python run_api.py`
- [ ] Tests pass: `python tests/test_system.py`
- [ ] New features test pass: `python tests/test_new_features.py`

---

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** - Look for error messages
2. **Review NEW_FEATURES.md** - For feature documentation
3. **Run tests** - Identify what's broken
4. **Check GitHub Issues** - See if others have the same problem
5. **Open an issue** - Include error messages and steps to reproduce

---

## 📚 Additional Resources

- [NEW_FEATURES.md](NEW_FEATURES.md) - Complete new features documentation
- [README.md](../README.md) - Updated main documentation
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - REST API reference
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide

---

## 🎉 Benefits of Migration

### Code Organization
- ✅ Clearer separation of concerns
- ✅ Easier to find specific functionality
- ✅ Better for team collaboration

### New Features
- ✅ Bulk operations save time
- ✅ Advanced analytics provide insights
- ✅ Automated invoicing reduces manual work

### Maintainability
- ✅ Easier to add new features
- ✅ Better test organization
- ✅ Improved documentation structure

---

**Version:** 2.1.0  
**Migration Difficulty:** Easy (No database changes required)  
**Estimated Time:** 5-10 minutes  
**Breaking Changes:** Import paths only (app.py works unchanged)

---

**Questions?** Open an issue on GitHub or refer to the documentation.
