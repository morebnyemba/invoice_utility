# New Features Documentation

## Version 2.1.0 - Advanced Features Release

This document describes the new features added to the Invoice Utility in version 2.1.0.

---

## 📦 Bulk Operations

The bulk operations module provides efficient ways to perform operations on multiple invoices, clients, or other entities at once.

### Features

#### 1. Bulk Invoice Creation
Create multiple invoices in a single transaction.

**Usage:**
```python
from src.business.bulk_operations import BulkInvoiceOperations
from src.models.database import get_db_connection

# Prepare invoice data
invoice_data_list = [
    {
        'client_id': 'client1',
        'services': ['Web Development', 'Design'],
        'amounts': [1000, 500],
        'tax_rate': 10,
        'currency': 'USD',
        'notes': 'Monthly retainer'
    },
    {
        'client_id': 'client2',
        'services': ['Consulting'],
        'amounts': [2000],
        'tax_rate': 10,
        'currency': 'USD'
    }
]

# Create invoices
with get_db_connection() as conn:
    result = BulkInvoiceOperations.bulk_create_invoices(conn, invoice_data_list)
    print(f"Created {result['created_count']} invoices")
    if result['errors']:
        print(f"Errors: {result['errors']}")
```

#### 2. Bulk Status Updates
Update the status of multiple invoices at once.

**Usage:**
```python
# Mark multiple invoices as paid
invoice_ids = ['inv001', 'inv002', 'inv003']
with get_db_connection() as conn:
    result = BulkInvoiceOperations.bulk_update_status(conn, invoice_ids, 'paid')
    print(f"Updated {result['updated_count']} invoices")
```

#### 3. Bulk Invoice Deletion
Delete multiple invoices and their associated payments.

**Usage:**
```python
invoice_ids = ['inv001', 'inv002']
with get_db_connection() as conn:
    result = BulkInvoiceOperations.bulk_delete_invoices(conn, invoice_ids)
    print(f"Deleted {result['deleted_count']} invoices")
```

#### 4. Bulk Client Import
Import multiple clients from external data sources.

**Usage:**
```python
from src.business.bulk_operations import BulkClientOperations

clients_data = [
    {'name': 'Acme Corp', 'email': 'contact@acme.com', 'phone': '555-1234'},
    {'name': 'TechStart', 'email': 'info@techstart.com', 'phone': '555-5678'}
]

with get_db_connection() as conn:
    result = BulkClientOperations.bulk_import_clients(conn, clients_data)
    print(f"Imported {result['imported_count']} clients")
```

#### 5. Bulk Reporting
Generate consolidated reports for multiple invoices.

**Usage:**
```python
from src.business.bulk_operations import BulkReporting

invoice_ids = ['inv001', 'inv002', 'inv003']
with get_db_connection() as conn:
    report = BulkReporting.generate_bulk_report(conn, invoice_ids)
    print(f"Total Amount: ${report['total_amount']}")
    print(f"Total Paid: ${report['total_paid']}")
    print(f"Total Outstanding: ${report['total_outstanding']}")
```

---

## 📊 Advanced Reporting & Analytics

The advanced reporting module provides comprehensive analytics and predictive insights.

### Features

#### 1. Revenue Trend Analysis
Analyze revenue trends over time with growth calculations.

**Usage:**
```python
from src.business.advanced_reporting import AdvancedReporting

with get_db_connection() as conn:
    trends = AdvancedReporting.revenue_trend_analysis(conn, months=12)
    print(f"Total Revenue: ${trends['total_revenue']}")
    print(f"Avg Monthly Revenue: ${trends['avg_monthly_revenue']}")
    print(f"Growth Rate: {trends['growth_rate']:.2f}%")
    
    # Access monthly data
    for month, data in trends['monthly_data'].items():
        print(f"{month}: ${data['revenue']}")
```

#### 2. Expense Breakdown Analysis
Categorize and analyze expenses with percentages.

**Usage:**
```python
with get_db_connection() as conn:
    breakdown = AdvancedReporting.expense_breakdown_analysis(conn)
    
    for category, data in breakdown['category_breakdown'].items():
        print(f"{category}: ${data['total']} ({data['percentage']:.1f}%)")
```

#### 3. Client Performance Metrics
Analyze client lifetime value and engagement.

**Usage:**
```python
with get_db_connection() as conn:
    metrics = AdvancedReporting.client_performance_metrics(conn, top_n=10)
    
    print(f"Total Clients: {metrics['total_clients']}")
    print(f"Active Clients: {metrics['active_clients']}")
    
    print("\nTop 10 Clients:")
    for client in metrics['top_clients']:
        print(f"{client['name']}: ${client['total_revenue']}")
```

#### 4. Project Profitability Analysis
Analyze profit margins and budget utilization by project.

**Usage:**
```python
with get_db_connection() as conn:
    profitability = AdvancedReporting.project_profitability_analysis(conn)
    
    for project in profitability['projects']:
        print(f"Project: {project['name']}")
        print(f"  Revenue: ${project['revenue']}")
        print(f"  Expenses: ${project['expenses']}")
        print(f"  Profit: ${project['profit']} ({project['profit_margin']:.1f}%)")
```

#### 5. Predictive Analytics
Forecast future revenue based on historical data.

**Usage:**
```python
with get_db_connection() as conn:
    predictions = AdvancedReporting.predictive_analytics(conn)
    
    print(f"Predicted Next Month: ${predictions['predicted_next_month']:.2f}")
    print(f"Predicted Next Quarter: ${predictions['predicted_next_quarter']:.2f}")
    print(f"Confidence Score: {predictions['confidence_score']:.1f}%")
```

#### 6. Invoice Aging Report
Track overdue invoices by age brackets.

**Usage:**
```python
with get_db_connection() as conn:
    aging = AdvancedReporting.invoice_aging_report(conn)
    
    print(f"Total Outstanding: ${aging['total_outstanding']}")
    
    for bucket_name, bucket_data in aging['aging_buckets'].items():
        print(f"\n{bucket_name}:")
        print(f"  Count: {bucket_data['count']}")
        print(f"  Amount: ${bucket_data['amount']}")
```

---

## 🤖 Automated Invoice Scheduler

The scheduler module automates recurring invoice generation and notifications.

### Features

#### 1. Automatic Recurring Invoice Generation
Automatically generates invoices based on recurring schedules.

**Setup:**
```python
from src.business.scheduler import InvoiceScheduler
from src.models.database import get_db_connection

# Initialize scheduler
scheduler = InvoiceScheduler(get_db_connection)

# Start background scheduler (checks every hour)
scheduler.start(check_interval=3600)

# The scheduler will automatically generate invoices based on:
# - Weekly schedules
# - Monthly schedules
# - Quarterly schedules
# - Yearly schedules
```

#### 2. Manual Invoice Generation
Manually trigger invoice generation for a specific recurring invoice.

**Usage:**
```python
scheduler = InvoiceScheduler(get_db_connection)
result = scheduler.manual_generate('recurring_invoice_id')

if result['success']:
    print(f"Generated invoice: {result['invoice_id']}")
else:
    print(f"Error: {result['error']}")
```

#### 3. View Upcoming Invoices
See which invoices will be generated in the near future.

**Usage:**
```python
scheduler = InvoiceScheduler(get_db_connection)
upcoming = scheduler.get_upcoming_invoices(days_ahead=30)

print(f"Upcoming invoices in next 30 days: {upcoming['count']}")
for invoice in upcoming['upcoming_invoices']:
    print(f"  {invoice['client_name']}: ${invoice['amount']}")
    print(f"    Due: {invoice['next_generation_date']}")
```

#### 4. Process All Due Invoices
Manually trigger processing of all due recurring invoices.

**Usage:**
```python
scheduler = InvoiceScheduler(get_db_connection)
result = scheduler.process_recurring_invoices()

print(f"Generated {result['generated_count']} invoices")
if result['errors']:
    print(f"Errors encountered: {len(result['errors'])}")
```

---

## 📧 Notification Manager

Automated email notifications for invoices.

### Features

#### 1. Send Invoice Notifications
Send notifications when invoices are created or updated.

**Usage:**
```python
from src.business.scheduler import NotificationManager

notification_mgr = NotificationManager(get_db_connection)

# Send creation notification
result = notification_mgr.send_invoice_notification('invoice_id', 'created')

# Send reminder notification
result = notification_mgr.send_invoice_notification('invoice_id', 'reminder')

# Send overdue notification
result = notification_mgr.send_invoice_notification('invoice_id', 'overdue')
```

#### 2. Batch Send Reminders
Send reminders for all overdue invoices.

**Usage:**
```python
notification_mgr = NotificationManager(get_db_connection)

# Send reminders for invoices overdue by 7+ days
result = notification_mgr.send_batch_reminders(days_overdue=7)

print(f"Sent {result['sent_count']} reminders")
```

---

## 🏗️ Integration with Existing Application

### Adding to Streamlit App

The new features can be integrated into the existing Streamlit app by importing the modules:

```python
# In app.py
from src.business.bulk_operations import BulkInvoiceOperations
from src.business.advanced_reporting import AdvancedReporting
from src.business.scheduler import InvoiceScheduler

# Add new menu items
menu_option = st.sidebar.selectbox("Menu", [
    "Dashboard",
    "Create Invoice",
    "Manage Invoices",
    "Bulk Operations",  # NEW
    "Advanced Reports",  # NEW
    "Recurring Invoices",
    "Settings"
])

if menu_option == "Bulk Operations":
    # Bulk operations UI
    pass
elif menu_option == "Advanced Reports":
    # Advanced reporting UI
    pass
```

### Adding to REST API

Add new endpoints for the features:

```python
# In src/api/api.py
from src.business.bulk_operations import BulkInvoiceOperations
from src.business.advanced_reporting import AdvancedReporting

@app.route('/api/v1/bulk/invoices', methods=['POST'])
@require_api_key
def bulk_create_invoices():
    data = request.json
    with get_db_connection() as conn:
        result = BulkInvoiceOperations.bulk_create_invoices(conn, data)
        return jsonify(result)

@app.route('/api/v1/reports/trends', methods=['GET'])
@require_api_key
def revenue_trends():
    months = request.args.get('months', 12, type=int)
    with get_db_connection() as conn:
        result = AdvancedReporting.revenue_trend_analysis(conn, months)
        return jsonify(result)
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Scheduler Configuration
SCHEDULER_CHECK_INTERVAL=3600  # How often to check for recurring invoices (seconds)
SCHEDULER_ENABLED=true         # Enable/disable scheduler

# Notification Configuration
NOTIFICATION_ENABLED=true      # Enable/disable notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Database Requirements

The new features use the existing database schema with these tables:
- `recurring_invoices` - For recurring invoice schedules
- `audit_logs` - For tracking notifications and actions
- `expenses` - For expense analysis
- `projects` - For project profitability

All tables are created automatically by the enhanced schema initialization.

---

## 🧪 Testing

Run the test suite to verify the new features:

```bash
# Test all new features
python tests/test_new_features.py

# Test the full system including new features
python tests/test_system.py
```

---

## 📈 Performance Considerations

### Bulk Operations
- Bulk operations use transactions for atomicity
- Large batches (>1000 items) should be split into smaller chunks
- Error handling is per-item to allow partial success

### Advanced Reporting
- Revenue trend analysis can be resource-intensive for large datasets
- Consider caching report results for frequently accessed data
- Use date range filters to limit data processing

### Scheduler
- Default check interval is 1 hour (3600 seconds)
- Runs in a background thread (daemon)
- Minimal resource usage when idle

---

## 🆘 Troubleshooting

### Scheduler Not Generating Invoices
1. Check that recurring invoices are marked as `is_active = 1`
2. Verify the `start_date` is in the past
3. Check `last_generated` date to ensure interval has passed
4. Review logs for errors

### Bulk Operations Failing
1. Check database connection
2. Verify data format matches expected structure
3. Review error details in the returned `errors` array
4. Ensure foreign keys (client_id, project_id) are valid

### Reports Showing No Data
1. Ensure there is data in the specified date range
2. Check that invoices have proper `created_at` timestamps
3. Verify database query permissions

---

## 📝 API Reference

Complete API documentation for the new modules:

### BulkInvoiceOperations
- `bulk_create_invoices(conn, invoice_data_list)` → Dict
- `bulk_update_status(conn, invoice_ids, new_status)` → Dict
- `bulk_delete_invoices(conn, invoice_ids)` → Dict
- `bulk_send_emails(conn, invoice_ids, email_settings)` → Dict

### BulkClientOperations
- `bulk_import_clients(conn, clients_data)` → Dict
- `bulk_update_clients(conn, updates)` → Dict

### BulkReporting
- `generate_bulk_report(conn, invoice_ids)` → Dict

### AdvancedReporting
- `revenue_trend_analysis(conn, months)` → Dict
- `expense_breakdown_analysis(conn, start_date, end_date)` → Dict
- `client_performance_metrics(conn, top_n)` → Dict
- `project_profitability_analysis(conn)` → Dict
- `predictive_analytics(conn)` → Dict
- `invoice_aging_report(conn)` → Dict

### InvoiceScheduler
- `start(check_interval)` → None
- `stop()` → None
- `process_recurring_invoices()` → Dict
- `manual_generate(recurring_invoice_id)` → Dict
- `get_upcoming_invoices(days_ahead)` → Dict

### NotificationManager
- `send_invoice_notification(invoice_id, notification_type)` → Dict
- `send_batch_reminders(days_overdue)` → Dict

---

## 🎯 Best Practices

1. **Always use transactions** for bulk operations
2. **Cache report data** when possible
3. **Run scheduler in production** as a system service
4. **Monitor notification logs** in audit_logs table
5. **Regular database maintenance** for optimal performance
6. **Test with sample data** before production use

---

**Version:** 2.1.0  
**Last Updated:** January 2026  
**Author:** Moreblessing Nyemba
