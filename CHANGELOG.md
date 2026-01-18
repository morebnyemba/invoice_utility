# Changelog

All notable changes to the Invoice Utility project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-01-18

### 🎉 Major Release - Advanced Features & Code Organization

This release introduces significant improvements to code organization and adds powerful new features for bulk operations, advanced analytics, and automation.

### Added

#### Code Organization
- **Folder Structure**: Reorganized entire codebase into logical folders
  - `/src/models/` - Database layer (database.py, db_schema.py)
  - `/src/business/` - Business logic modules
  - `/src/api/` - REST API endpoints
  - `/src/utils/` - Utility functions
  - `/tests/` - Test suite
  - `/docs/` - Documentation files
- **Package Init Files**: Added proper Python package structure with `__init__.py` files
- **Entry Points**: Created `run_api.py` as the new API server entry point

#### New Features - Bulk Operations
- **Bulk Invoice Creation**: Create multiple invoices in a single transaction
- **Bulk Status Updates**: Update status for multiple invoices at once
- **Bulk Invoice Deletion**: Delete multiple invoices and their payments
- **Bulk Client Import**: Import multiple clients from external data
- **Bulk Client Updates**: Update multiple client records
- **Bulk Email Sending**: Send emails to multiple invoice clients
- **Bulk Reporting**: Generate consolidated reports for multiple invoices

#### New Features - Advanced Reporting
- **Revenue Trend Analysis**: Analyze revenue trends over time with growth calculations
- **Expense Breakdown**: Categorize and analyze expenses by category with percentages
- **Client Performance Metrics**: Calculate client lifetime value and engagement metrics
- **Project Profitability Analysis**: Analyze profit margins and budget utilization
- **Predictive Analytics**: Forecast future revenue based on historical data
- **Invoice Aging Reports**: Track overdue invoices by age brackets (current, 1-30, 31-60, 61-90, 90+ days)

#### New Features - Automation
- **Invoice Scheduler**: Automated recurring invoice generation system
- **Background Processing**: Daemon thread for continuous scheduling
- **Manual Generation**: Trigger invoice generation on demand
- **Upcoming Invoices View**: See which invoices will be generated soon
- **Notification Manager**: Automated email notifications for invoices
- **Batch Reminders**: Send reminders for all overdue invoices
- **Audit Logging**: Track all automated actions in audit_logs table

#### Documentation
- **NEW_FEATURES.md**: Comprehensive documentation for all new features
- **MIGRATION_GUIDE.md**: Step-by-step guide for migrating to new structure
- **CHANGELOG.md**: This file - tracking all changes

#### Testing
- **test_new_features.py**: Test suite for all new features
- **Enhanced test_system.py**: Updated to work with new folder structure

### Changed

- **Import Paths**: All imports updated to use new folder structure
  - `from database import ...` → `from src.models.database import ...`
  - `from business_logic import ...` → `from src.business.business_logic import ...`
  - `from api import ...` → `from src.api.api import ...`
- **API Server**: Start command changed from `python api.py` to `python run_api.py`
- **Gunicorn Command**: Changed to `gunicorn -w 4 -b 0.0.0.0:5000 src.api.api:app`
- **README**: Updated with new folder structure and features
- **Roadmap**: Marked completed features (REST API, Bulk Operations, Advanced Reporting, Automated Invoices)

### Fixed

- **Module Organization**: Better separation of concerns
- **Import Consistency**: All imports now use consistent paths
- **Test Paths**: Tests updated to import from correct locations

### Deprecated

- **Direct module imports**: Old import paths (e.g., `from database import ...`) are deprecated
  - Still work but should be updated to new paths
  - No breaking changes - app.py continues to work

### Performance

- **No degradation**: Code reorganization has no performance impact
- **Bulk operations**: More efficient than individual operations
- **Scheduler**: Minimal resource usage in background

### Compatibility

- **Database**: 100% compatible with existing databases
- **No migration required**: Existing data works without changes
- **Backward compatible**: Old code still works with deprecation warnings

### Security

- **No new vulnerabilities**: All security features maintained
- **Enhanced audit logging**: Better tracking of automated actions
- **Same authentication**: No changes to auth system

---

## [2.0.0] - 2026-01-15

### Added - Enterprise Features

#### Multi-Database Support
- **SQLite**: Default database (no setup required)
- **PostgreSQL**: Production-grade relational database support
- **MySQL**: Popular open-source database support
- **Connection Pooling**: For better performance with PostgreSQL/MySQL
- **Database Abstraction Layer**: Clean API for all database types
- **Automatic Fallback**: Gracefully fall back to SQLite if others unavailable

#### Business Logic Features
- **Invoice Templates**: Save and reuse frequently used service combinations
- **Recurring Invoices**: Automated subscription billing (weekly/monthly/quarterly/yearly)
- **Tax Calculation**: VAT/GST/Sales Tax support with configurable rates
- **Multi-Currency Support**: Handle international invoicing
- **Role-Based Access Control**: Admin, Manager, Accountant, Viewer roles
- **Audit Logging**: Complete trail of all business actions
- **Invoice Reminders**: Track and send overdue payment reminders
- **Business Analytics**: Calculate key metrics (revenue, expenses, profit, LTV)

#### REST API
- **Full HTTP API**: All operations available via REST endpoints
- **JSON Format**: Standard request/response format
- **API Key Authentication**: Secure API key-based auth
- **ERP Integration Ready**: Connect with external accounting systems

#### Documentation
- **DATABASE_SETUP.md**: Comprehensive database configuration guide
- **API_DOCUMENTATION.md**: Complete API reference
- **ENHANCEMENTS.md**: Detailed enhancement summary
- **FIRST_TIME_SETUP.md**: First-time configuration guide
- **OFFLINE_GUIDE.md**: Offline operation details
- **QUICKSTART.md**: 5-minute quick start guide

#### Testing
- **test_system.py**: Automated system testing script
- **Module Import Tests**: Verify all modules load correctly
- **Database Connection Tests**: Test connectivity to all database types
- **Business Logic Tests**: Verify tax, currency, and other calculations

### Changed

- **Database Schema**: Enhanced with new tables for templates, recurring invoices, audit logs
- **User Table**: Added `role` column for RBAC
- **Invoice Table**: Added `currency`, `tax_rate`, `tax_amount` columns
- **Settings Management**: Improved configuration through environment variables

### Documentation

- **README**: Completely rewritten with comprehensive feature documentation
- **License**: Added MIT License with attribution requirement

---

## [1.0.0] - Initial Release

### Added

#### Core Features
- **Invoice Management**: Create, edit, view, delete invoices
- **Client Management**: Manage client information
- **Project Management**: Link invoices to projects
- **Payment Tracking**: Record and track payments
- **PDF Generation**: Professional invoice PDFs with ReportLab
- **Invoice Sharing**: Secure sharing links with expiration
- **Email Integration**: Send invoices via SMTP

#### User Interface
- **Streamlit App**: Modern web interface
- **Dashboard**: Overview of key metrics
- **Invoice Creation**: Intuitive invoice creation form
- **Client Management**: Easy client CRUD operations
- **Settings**: Configure company information and SMTP

#### Database
- **SQLite**: Simple file-based database
- **Core Tables**: users, clients, projects, invoices, payments, settings

#### Security
- **Password Hashing**: bcrypt for secure password storage
- **Input Validation**: Basic validation and sanitization
- **Session Management**: Streamlit session state

#### Reporting
- **Basic Analytics**: Revenue, expenses, outstanding invoices
- **Charts**: Plotly charts for visualization
- **CSV Export**: Export data to CSV files

---

## Version Comparison

| Feature | v1.0.0 | v2.0.0 | v2.1.0 |
|---------|--------|--------|--------|
| Basic Invoicing | ✅ | ✅ | ✅ |
| PDF Generation | ✅ | ✅ | ✅ |
| SQLite Support | ✅ | ✅ | ✅ |
| PostgreSQL Support | ❌ | ✅ | ✅ |
| MySQL Support | ❌ | ✅ | ✅ |
| REST API | ❌ | ✅ | ✅ |
| Invoice Templates | ❌ | ✅ | ✅ |
| Recurring Invoices | ❌ | ✅ | ✅ |
| Tax Calculation | ❌ | ✅ | ✅ |
| Multi-Currency | ❌ | ✅ | ✅ |
| RBAC | ❌ | ✅ | ✅ |
| Audit Logging | ❌ | ✅ | ✅ |
| **Bulk Operations** | ❌ | ❌ | ✅ |
| **Advanced Analytics** | ❌ | ❌ | ✅ |
| **Automated Scheduler** | ❌ | ❌ | ✅ |
| **Predictive Forecasting** | ❌ | ❌ | ✅ |
| **Organized Code Structure** | ❌ | ❌ | ✅ |

---

## Upgrade Paths

### From v1.0.0 to v2.1.0
1. Backup your database
2. Pull latest changes
3. Update imports to new structure (see MIGRATION_GUIDE.md)
4. Run `python tests/test_system.py` to verify
5. Start using new features!

### From v2.0.0 to v2.1.0
1. Pull latest changes
2. Update imports to new structure (see MIGRATION_GUIDE.md)
3. No database migration needed
4. Run tests to verify
5. Start using new features!

---

## Future Roadmap

### Planned for v2.2.0
- [ ] Mobile responsive design improvements
- [ ] Payment gateway integrations (Stripe, PayPal)
- [ ] Multi-language support (i18n)
- [ ] Enhanced invoice customization UI

### Planned for v3.0.0
- [ ] Client portal access
- [ ] SMS notifications
- [ ] Mobile app (React Native)
- [ ] Advanced inventory management

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

---

## License

This project is licensed under the MIT License with attribution requirement.
See [LICENSE](../LICENSE) for full details.

---

**For detailed migration instructions, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)**

**For new features documentation, see [NEW_FEATURES.md](NEW_FEATURES.md)**
