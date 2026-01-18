"""
Enhanced business logic features for the invoice utility
"""
import datetime
import uuid
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import json

# ---------- INVOICE TEMPLATES ----------
class InvoiceTemplate:
    """Class for managing invoice templates"""
    
    @staticmethod
    def create_template(conn, name: str, services: List[Tuple[str, float]], 
                       description: str = "", is_default: bool = False):
        """Create a new invoice template"""
        template_id = str(uuid.uuid4())[:8]
        created_at = datetime.datetime.now().isoformat()
        
        conn.execute(
            """INSERT INTO invoice_templates 
               (id, name, services, description, is_default, created_at) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (template_id, name, str(services), description, is_default, created_at)
        )
        conn.commit()
        return template_id
    
    @staticmethod
    def get_all_templates(conn):
        """Get all invoice templates"""
        return conn.execute(
            "SELECT * FROM invoice_templates ORDER BY is_default DESC, name ASC"
        ).fetchall()
    
    @staticmethod
    def get_template_by_id(conn, template_id: str):
        """Get a specific template by ID"""
        return conn.execute(
            "SELECT * FROM invoice_templates WHERE id = ?",
            (template_id,)
        ).fetchone()


# ---------- RECURRING INVOICES ----------
class RecurringInvoice:
    """Class for managing recurring invoices and subscriptions"""
    
    FREQUENCIES = ["weekly", "monthly", "quarterly", "yearly"]
    
    @staticmethod
    def create_recurring(conn, client_id: str, services: List[Tuple[str, float]], 
                        frequency: str, start_date: str, end_date: Optional[str] = None,
                        project_id: Optional[str] = None):
        """Create a recurring invoice schedule"""
        if frequency not in RecurringInvoice.FREQUENCIES:
            raise ValueError(f"Frequency must be one of {RecurringInvoice.FREQUENCIES}")
        
        recurring_id = str(uuid.uuid4())[:8]
        total = sum(price for _, price in services)
        created_at = datetime.datetime.now().isoformat()
        
        conn.execute(
            """INSERT INTO recurring_invoices 
               (id, client_id, project_id, services, total, frequency, 
                start_date, end_date, is_active, created_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (recurring_id, client_id, project_id, str(services), total, 
             frequency, start_date, end_date, True, created_at)
        )
        conn.commit()
        return recurring_id
    
    @staticmethod
    def get_due_recurring_invoices(conn, check_date: Optional[str] = None):
        """Get recurring invoices that are due for generation"""
        if not check_date:
            check_date = datetime.date.today().isoformat()
        
        return conn.execute(
            """SELECT * FROM recurring_invoices 
               WHERE is_active = 1 
               AND start_date <= ? 
               AND (end_date IS NULL OR end_date >= ?)
               AND (last_generated IS NULL OR last_generated < ?)""",
            (check_date, check_date, check_date)
        ).fetchall()
    
    @staticmethod
    def calculate_next_date(last_date: str, frequency: str) -> str:
        """Calculate the next invoice date based on frequency"""
        last = datetime.datetime.fromisoformat(last_date).date()
        
        if frequency == "weekly":
            next_date = last + datetime.timedelta(weeks=1)
        elif frequency == "monthly":
            # Add one month
            if last.month == 12:
                next_date = last.replace(year=last.year + 1, month=1)
            else:
                next_date = last.replace(month=last.month + 1)
        elif frequency == "quarterly":
            # Add 3 months
            month = last.month + 3
            year = last.year
            while month > 12:
                month -= 12
                year += 1
            next_date = last.replace(year=year, month=month)
        elif frequency == "yearly":
            next_date = last.replace(year=last.year + 1)
        else:
            raise ValueError(f"Unknown frequency: {frequency}")
        
        return next_date.isoformat()


# ---------- TAX CALCULATION ----------
class TaxCalculator:
    """Tax calculation utilities"""
    
    @staticmethod
    def calculate_tax(amount: float, tax_rate: float, tax_type: str = "VAT") -> Dict:
        """
        Calculate tax on an amount
        
        Args:
            amount: The base amount
            tax_rate: Tax rate as percentage (e.g., 15 for 15%)
            tax_type: Type of tax (VAT, GST, Sales Tax, etc.)
        
        Returns:
            Dictionary with subtotal, tax_amount, and total
        """
        tax_amount = amount * (tax_rate / 100)
        total = amount + tax_amount
        
        return {
            "subtotal": round(amount, 2),
            "tax_type": tax_type,
            "tax_rate": tax_rate,
            "tax_amount": round(tax_amount, 2),
            "total": round(total, 2)
        }
    
    @staticmethod
    def get_tax_settings(conn) -> Dict:
        """Get tax settings from database"""
        settings = {}
        rows = conn.execute(
            "SELECT key, value FROM settings WHERE key LIKE 'TAX_%'"
        ).fetchall()
        
        for row in rows:
            settings[row['key']] = row['value']
        
        return settings


# ---------- CURRENCY SUPPORT ----------
class CurrencyConverter:
    """Multi-currency support"""
    
    # Default exchange rates (should be updated regularly in production)
    DEFAULT_RATES = {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.73,
        "ZWL": 322.0,  # Zimbabwe Dollar
        "ZAR": 18.5,   # South African Rand
    }
    
    @staticmethod
    def convert(amount: float, from_currency: str, to_currency: str, 
                rates: Optional[Dict] = None) -> float:
        """Convert amount from one currency to another"""
        if rates is None:
            rates = CurrencyConverter.DEFAULT_RATES
        
        if from_currency not in rates or to_currency not in rates:
            raise ValueError(f"Currency not supported")
        
        # Convert to USD first, then to target currency
        usd_amount = amount / rates[from_currency]
        converted = usd_amount * rates[to_currency]
        
        return round(converted, 2)
    
    @staticmethod
    def format_currency(amount: float, currency: str) -> str:
        """Format amount with currency symbol"""
        symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "ZWL": "ZWL$",
            "ZAR": "R"
        }
        
        symbol = symbols.get(currency, currency)
        return f"{symbol}{amount:,.2f}"


# ---------- AUDIT LOGGING ----------
class AuditLog:
    """Audit logging for business actions"""
    
    @staticmethod
    def log_action(conn, username: str, action: str, entity_type: str, 
                   entity_id: str, details: Optional[str] = None):
        """Log a business action for audit trail"""
        log_id = str(uuid.uuid4())[:8]
        timestamp = datetime.datetime.now().isoformat()
        
        conn.execute(
            """INSERT INTO audit_logs 
               (id, username, action, entity_type, entity_id, details, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (log_id, username, action, entity_type, entity_id, details, timestamp)
        )
        conn.commit()
    
    @staticmethod
    def get_logs(conn, entity_type: Optional[str] = None, 
                 entity_id: Optional[str] = None, limit: int = 100):
        """Retrieve audit logs with optional filtering"""
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        if entity_id:
            query += " AND entity_id = ?"
            params.append(entity_id)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        return conn.execute(query, tuple(params)).fetchall()


# ---------- ROLE-BASED ACCESS CONTROL ----------
class RoleManager:
    """Role-based access control"""
    
    ROLES = ["admin", "manager", "accountant", "viewer"]
    
    PERMISSIONS = {
        "admin": ["*"],  # All permissions
        "manager": [
            "view_dashboard", "create_invoice", "view_invoices", 
            "manage_clients", "manage_projects", "view_reports"
        ],
        "accountant": [
            "view_dashboard", "create_invoice", "view_invoices", 
            "manage_expenses", "view_reports", "record_payment"
        ],
        "viewer": ["view_dashboard", "view_invoices", "view_reports"]
    }
    
    @staticmethod
    def assign_role(conn, username: str, role: str):
        """Assign a role to a user"""
        if role not in RoleManager.ROLES:
            raise ValueError(f"Invalid role. Must be one of {RoleManager.ROLES}")
        
        conn.execute(
            "UPDATE users SET role = ? WHERE username = ?",
            (role, username)
        )
        conn.commit()
    
    @staticmethod
    def has_permission(conn, username: str, permission: str) -> bool:
        """Check if a user has a specific permission"""
        user = conn.execute(
            "SELECT role FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        
        if not user or 'role' not in user:
            return False
        
        role = user['role']
        
        # Admin has all permissions
        if role == "admin" or "*" in RoleManager.PERMISSIONS.get(role, []):
            return True
        
        return permission in RoleManager.PERMISSIONS.get(role, [])


# ---------- INVOICE REMINDERS ----------
class InvoiceReminder:
    """Automated invoice reminder system"""
    
    @staticmethod
    def get_overdue_invoices(conn, days_overdue: int = 7):
        """Get invoices that are overdue by specified days"""
        cutoff_date = (
            datetime.date.today() - datetime.timedelta(days=days_overdue)
        ).strftime('%d %B %Y')
        
        return conn.execute(
            """SELECT i.*, c.name, c.email 
               FROM invoices i
               JOIN clients c ON i.client_id = c.id
               WHERE i.status = 'unpaid' 
               AND i.date <= ?""",
            (cutoff_date,)
        ).fetchall()
    
    @staticmethod
    def create_reminder(conn, invoice_id: str, reminder_type: str, sent_date: str):
        """Record that a reminder was sent"""
        reminder_id = str(uuid.uuid4())[:8]
        created_at = datetime.datetime.now().isoformat()
        
        conn.execute(
            """INSERT INTO invoice_reminders 
               (id, invoice_id, reminder_type, sent_date, created_at) 
               VALUES (?, ?, ?, ?, ?)""",
            (reminder_id, invoice_id, reminder_type, sent_date, created_at)
        )
        conn.commit()


# ---------- ENHANCED REPORTING ----------
class BusinessAnalytics:
    """Advanced business analytics and reporting"""
    
    @staticmethod
    def calculate_metrics(conn, start_date: str, end_date: str) -> Dict:
        """Calculate key business metrics for a date range"""
        # Revenue
        revenue_result = conn.execute(
            """SELECT SUM(total) as total_revenue, COUNT(*) as invoice_count
               FROM invoices 
               WHERE status = 'paid' AND date BETWEEN ? AND ?""",
            (start_date, end_date)
        ).fetchone()
        
        # Expenses
        expenses_result = conn.execute(
            """SELECT SUM(amount) as total_expenses
               FROM expenses 
               WHERE date BETWEEN ? AND ?""",
            (start_date, end_date)
        ).fetchone()
        
        # Outstanding
        outstanding_result = conn.execute(
            """SELECT SUM(total) as outstanding
               FROM invoices 
               WHERE status = 'unpaid'"""
        ).fetchone()
        
        revenue = revenue_result['total_revenue'] or 0
        expenses = expenses_result['total_expenses'] or 0
        
        return {
            "revenue": revenue,
            "expenses": expenses,
            "profit": revenue - expenses,
            "outstanding": outstanding_result['outstanding'] or 0,
            "invoice_count": revenue_result['invoice_count'] or 0,
            "profit_margin": (revenue - expenses) / revenue * 100 if revenue > 0 else 0
        }
