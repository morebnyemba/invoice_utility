"""
Database schema initialization and migration utilities
"""
from database import get_db_connection, is_sqlite
import sqlite3


def init_enhanced_schema():
    """Initialize enhanced database schema with business features"""
    with get_db_connection() as conn:
        cursor = conn.cursor() if is_sqlite() else None
        
        # Base tables (existing)
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, 
            password TEXT NOT NULL, 
            role TEXT DEFAULT 'admin',
            created_at TEXT
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY, 
            name TEXT NOT NULL, 
            email TEXT, 
            phone TEXT, 
            created_at TEXT
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY, 
            client_id TEXT NOT NULL, 
            name TEXT NOT NULL, 
            budget REAL, 
            status TEXT, 
            description TEXT, 
            created_at TEXT, 
            FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS invoices (
            id TEXT PRIMARY KEY, 
            client_id TEXT NOT NULL, 
            project_id TEXT, 
            services TEXT, 
            total REAL, 
            date TEXT, 
            status TEXT DEFAULT 'unpaid', 
            currency TEXT DEFAULT 'USD',
            tax_rate REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            created_at TEXT, 
            FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE, 
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS shared_invoices (
            id TEXT PRIMARY KEY, 
            invoice_id TEXT NOT NULL, 
            access_token TEXT NOT NULL, 
            expiry_date TEXT, 
            created_at TEXT, 
            FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, 
            value TEXT
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS expenses (
            id TEXT PRIMARY KEY, 
            date TEXT NOT NULL, 
            category TEXT NOT NULL, 
            description TEXT, 
            amount REAL NOT NULL, 
            created_at TEXT
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY, 
            invoice_id TEXT NOT NULL, 
            amount REAL NOT NULL, 
            date TEXT, 
            method TEXT, 
            notes TEXT, 
            created_at TEXT, 
            FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
        )''')
        
        # New business feature tables
        conn.execute('''CREATE TABLE IF NOT EXISTS invoice_templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            services TEXT NOT NULL,
            description TEXT,
            is_default INTEGER DEFAULT 0,
            created_at TEXT
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS recurring_invoices (
            id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            project_id TEXT,
            services TEXT NOT NULL,
            total REAL NOT NULL,
            frequency TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            last_generated TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS invoice_reminders (
            id TEXT PRIMARY KEY,
            invoice_id TEXT NOT NULL,
            reminder_type TEXT NOT NULL,
            sent_date TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
        )''')
        
        # API Keys Table for REST API authentication
        conn.execute('''CREATE TABLE IF NOT EXISTS api_keys (
            key TEXT PRIMARY KEY,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL,
            last_used TEXT
        )''')
        
        # Migration: Add new columns to existing tables
        try:
            conn.execute("SELECT role FROM users LIMIT 1")
        except:
            try:
                conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'admin'")
            except:
                pass
        
        try:
            conn.execute("SELECT currency FROM invoices LIMIT 1")
        except:
            try:
                conn.execute("ALTER TABLE invoices ADD COLUMN currency TEXT DEFAULT 'USD'")
            except:
                pass
        
        try:
            conn.execute("SELECT tax_rate FROM invoices LIMIT 1")
        except:
            try:
                conn.execute("ALTER TABLE invoices ADD COLUMN tax_rate REAL DEFAULT 0")
                conn.execute("ALTER TABLE invoices ADD COLUMN tax_amount REAL DEFAULT 0")
            except:
                pass
        
        conn.commit()


def add_default_tax_settings(conn):
    """Add default tax settings"""
    defaults = {
        "TAX_ENABLED": "false",
        "TAX_TYPE": "VAT",
        "TAX_RATE": "15",
        "TAX_NUMBER": "",
    }
    
    for key, value in defaults.items():
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    conn.commit()


def check_database_health():
    """Check database connection and schema integrity"""
    try:
        with get_db_connection() as conn:
            # Check if all required tables exist
            required_tables = [
                'users', 'clients', 'projects', 'invoices', 
                'expenses', 'payments', 'settings'
            ]
            
            for table in required_tables:
                result = conn.execute(
                    f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
                    if is_sqlite() else
                    f"SELECT table_name FROM information_schema.tables WHERE table_name='{table}'"
                ).fetchone()
                
                if not result:
                    return False, f"Missing table: {table}"
            
            return True, "Database health check passed"
    except Exception as e:
        return False, f"Database health check failed: {str(e)}"
