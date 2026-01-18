import streamlit as st
import sqlite3
import uuid
import datetime
import os
import ast  # Used for safely evaluating string representations of lists
import pandas as pd
import hashlib # For password hashing
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus.flowables import HRFlowable
import plotly.express as px
import secrets # For generating secure tokens for sharing
import re
import time
from contextlib import contextmanager
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import bcrypt
import json

# Import enhanced database and business logic modules
try:
    from database import get_db_connection as get_db_conn_new, get_db_type, is_sqlite
    from db_schema import init_enhanced_schema, add_default_tax_settings, check_database_health
    from business_logic import (
        InvoiceTemplate, RecurringInvoice, TaxCalculator, CurrencyConverter,
        AuditLog, RoleManager, InvoiceReminder, BusinessAnalytics
    )
    USE_ENHANCED_FEATURES = True
except ImportError:
    USE_ENHANCED_FEATURES = False

# ---------- CONFIGURATION ----------
import os
from dataclasses import dataclass

@dataclass
class Config:
    DB_NAME: str = os.getenv("DB_NAME", "invoices.db")
    LOGO_PATH: str = os.getenv("LOGO_PATH", "logo.png")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

config = Config()
DB_NAME = config.DB_NAME
LOGO_PATH = config.LOGO_PATH

# ---------- SECURITY UTILITIES ----------
def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_password, provided_password):
    """Verifies a provided password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
    except Exception:
        return False

def validate_password(password):
    """Validate password meets complexity requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"

def validate_email(email):
    """Basic email validation"""
    if not email:  # Empty email is allowed (optional field)
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Basic phone validation"""
    if not phone:  # Empty phone is allowed (optional field)
        return True
    # Remove spaces, dashes, parentheses, and plus sign for checking
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    return cleaned.isdigit() and len(cleaned) >= 7

def sanitize_input(text):
    """Basic input sanitization to prevent XSS and SQL injection"""
    if not text:
        return text
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[;\"\']', '', str(text))
    return sanitized.strip()

# ---------- DATABASE UTILITIES ----------
@contextmanager
def get_db_connection():
    """Context manager for database connections with error handling"""
    # Use enhanced database connection if available
    if USE_ENHANCED_FEATURES:
        try:
            with get_db_conn_new() as conn:
                yield conn
            return
        except Exception as e:
            st.error(f"Enhanced database error: {e}")
            if config.DEBUG:
                st.error(f"Detailed error: {str(e)}")
            # Fall back to SQLite
    
    # Fallback to original SQLite connection
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        yield conn
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        if config.DEBUG:
            st.error(f"Detailed error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def init_db():
    """Initializes the database schema."""
    # Use enhanced schema if available
    if USE_ENHANCED_FEATURES:
        try:
            init_enhanced_schema()
            with get_db_connection() as conn:
                add_default_tax_settings(conn)
            return
        except Exception as e:
            st.warning(f"Could not initialize enhanced schema: {e}. Using basic schema.")
    
    # Original schema initialization
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Users Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT NOT NULL, created_at TEXT)''')
        # Clients Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS clients (id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT, phone TEXT, created_at TEXT)''')
        # Projects Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, client_id TEXT NOT NULL, name TEXT NOT NULL, budget REAL, status TEXT, description TEXT, created_at TEXT, FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE)''')
        # Invoices Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (id TEXT PRIMARY KEY, client_id TEXT NOT NULL, project_id TEXT, services TEXT, total REAL, date TEXT, status TEXT DEFAULT 'unpaid', created_at TEXT, FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE, FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL)''')
        # Shared Invoices Table (for secure sharing links)
        cursor.execute('''CREATE TABLE IF NOT EXISTS shared_invoices (id TEXT PRIMARY KEY, invoice_id TEXT NOT NULL, access_token TEXT NOT NULL, expiry_date TEXT, created_at TEXT, FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE)''')
        # Settings Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
        # Expenses Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (id TEXT PRIMARY KEY, date TEXT NOT NULL, category TEXT NOT NULL, description TEXT, amount REAL NOT NULL, created_at TEXT)''')
        # Payments Table (new)
        cursor.execute('''CREATE TABLE IF NOT EXISTS payments (id TEXT PRIMARY KEY, invoice_id TEXT NOT NULL, amount REAL NOT NULL, date TEXT, method TEXT, notes TEXT, created_at TEXT, FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE)''')

        # --- SCHEMA MIGRATION ---
        # Add project_id to invoices if it doesn't exist (for backward compatibility)
        try:
            cursor.execute("SELECT project_id FROM invoices LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE invoices ADD COLUMN project_id TEXT")
        
        # Add created_at columns if they don't exist
        for table in ['users', 'clients', 'projects', 'invoices', 'shared_invoices', 'expenses', 'payments']:
            try:
                cursor.execute(f"SELECT created_at FROM {table} LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN created_at TEXT")

        conn.commit()

def check_and_set_default_settings():
    """Checks for default settings and creates them if they don't exist."""
    defaults = {
        "COMPANY_NAME": "Slyker Tech Web Services",
        "COMPANY_ADDRESS": "2789 Dada Cresent, Budiriro 2, Harare, Zimbabwe",
        "COMPANY_PHONE": "+263787211325",
        "COMPANY_EMAIL": "info@slykertech.co.zw",
        "COMPANY_TIN": "TIN: 1001672571",
        "BANK_DETAILS": "<b>Payment Details:</b><br/>Ecocash: +263787211325 (Moreblessing Nyemba)<br/>Innbucks: +263787211325 (Moreblessing Nyemba)<br/>Omari: +263787211325 (Moreblessing Nyemba)<br/>",
        "SMTP_SERVER": "",
        "SMTP_PORT": "465",
        "SMTP_USERNAME": "",
        "SMTP_SENDER_EMAIL": "",
        "EMAIL_SUBJECT": "Invoice from {company_name}",
        "EMAIL_BODY": "Dear {client_name},<br><br>Please find attached your invoice {invoice_id} for a total of ${total}.<br><br>Thank you for your business!<br><br>Best regards,<br>{company_name}"
    }
    with get_db_connection() as conn:
        for key, value in defaults.items():
            conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()

# ---------- AUTHENTICATION UTILITIES ----------
def check_for_users():
    """Checks if any users exist in the database."""
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users LIMIT 1").fetchone()
    return user is not None

def check_session_timeout():
    """Check if the user session has timed out"""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        return True
    
    if 'login_time' not in st.session_state:
        return True
    
    elapsed_time = time.time() - st.session_state.login_time
    return elapsed_time > config.SESSION_TIMEOUT

# ---------- DATA FETCHING UTILITIES ----------
def fetch_settings():
    """Fetches all settings from the database and returns them as a dict."""
    with get_db_connection() as conn:
        settings_data = conn.execute("SELECT key, value FROM settings").fetchall()
    return {row['key']: row['value'] for row in settings_data}

def fetch_all_clients():
    """Fetches all clients from the database, ordered by name."""
    with get_db_connection() as conn:
        clients = conn.execute("SELECT * FROM clients ORDER BY name ASC").fetchall()
    return clients
    
def fetch_all_projects_with_client_info():
    """Fetches all projects with joined client names."""
    with get_db_connection() as conn:
        projects = conn.execute('''
            SELECT p.id, p.name, p.budget, p.status, p.description, c.name as client_name, c.id as client_id
            FROM projects p
            JOIN clients c ON p.client_id = c.id
            ORDER BY p.name ASC
        ''').fetchall()
    return projects

def fetch_all_invoices_with_client_info():
    """Fetches all invoices with joined client information."""
    with get_db_connection() as conn:
        invoices = conn.execute('''
            SELECT i.id, i.date, i.total, i.status, i.services, i.project_id, c.name, c.email, c.phone, c.id as client_id
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            ORDER BY i.date DESC
        ''').fetchall()
    return invoices

def fetch_invoice_by_id(invoice_id):
    """Fetches a single invoice by its ID, with client info."""
    with get_db_connection() as conn:
        invoice = conn.execute('''
            SELECT i.id, i.date, i.total, i.status, i.services, c.name, c.email, c.phone
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            WHERE i.id = ?
        ''', (invoice_id,)).fetchone()
    return invoice

def fetch_all_expenses():
    """Fetches all expenses from the database, ordered by date."""
    with get_db_connection() as conn:
        expenses = conn.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
    return expenses

def fetch_payments_for_invoice(invoice_id):
    """Fetches all payments for a specific invoice."""
    with get_db_connection() as conn:
        payments = conn.execute("SELECT * FROM payments WHERE invoice_id = ? ORDER BY date DESC", (invoice_id,)).fetchall()
    return payments

# ---------- PAYMENT MANAGEMENT ----------
def record_payment(invoice_id, amount, payment_date, method, notes=""):
    """Record a payment for an invoice"""
    with get_db_connection() as conn:
        payment_id = str(uuid.uuid4())[:8]
        created_at = datetime.datetime.now().isoformat()
        
        conn.execute(
            "INSERT INTO payments (id, invoice_id, amount, date, method, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (payment_id, invoice_id, amount, payment_date, method, notes, created_at)
        )
        
        # Update invoice status if fully paid
        invoice = conn.execute("SELECT total FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
        total_paid = conn.execute("SELECT SUM(amount) FROM payments WHERE invoice_id = ?", (invoice_id,)).fetchone()[0] or 0
        
        if total_paid >= invoice['total']:
            conn.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (invoice_id,))
        elif total_paid > 0:
            conn.execute("UPDATE invoices SET status = 'partially_paid' WHERE id = ?", (invoice_id,))
        
        conn.commit()

# ---------- BACKUP & DATA EXPORT ----------
def export_database_backup():
    """Create a backup of the database"""
    backup_filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    # Create backup using SQLite backup API
    with get_db_connection() as conn:
        backup_conn = sqlite3.connect(backup_filename)
        conn.backup(backup_conn)
        backup_conn.close()
    
    return backup_filename

# ---------- UI HELPER DECORATORS ----------
def with_loading(message="Processing..."):
    """Decorator to show loading spinner for long operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with st.spinner(message):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

# ---------- PDF GENERATION ----------
@with_loading("Generating PDF...")
def generate_invoice_pdf(invoice_data, settings):
    """Generates a professional PDF invoice from the provided data and settings."""
    filename = f"invoice_{invoice_data['id']}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(name='RightAlign', alignment=2))
    styles.add(ParagraphStyle(name='TotalLabel', alignment=2, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='TotalValue', alignment=2, fontName='Helvetica-Bold', textColor=colors.HexColor("#0057A0")))

    elements = []

    header_data = [[
        Image(LOGO_PATH, width=60, height=60) if os.path.exists(LOGO_PATH) else '',
        Paragraph(f"<b>{settings.get('COMPANY_NAME', '')}</b><br/>{settings.get('COMPANY_ADDRESS', '')}<br/>{settings.get('COMPANY_PHONE', '')} | {settings.get('COMPANY_EMAIL', '')}<br/>{settings.get('COMPANY_TIN', '')}", styles['RightAlign'])
    ]]
    header_table = Table(header_data, colWidths=[10*cm, 7.5*cm])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(header_table)

    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph("INVOICE", styles['h1']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Spacer(1, 0.5*cm))

    status_html = f"<font color='green'><b>PAID</b></font>" if invoice_data['status'] == 'paid' else f"<font color='red'><b>UNPAID</b></font>"
    details_data = [
        [Paragraph(f"<b>Bill To:</b><br/>{invoice_data['name']}<br/>{invoice_data['email'] or ''}<br/>{invoice_data['phone'] or ''}", styles['Normal']),
         Paragraph(f"<b>Invoice ID:</b> {invoice_data['id']}<br/><b>Date:</b> {invoice_data['date']}<br/><b>Status:</b> {status_html}", styles['RightAlign'])]
    ]
    details_table = Table(details_data, colWidths=[9*cm, 8.5*cm])
    details_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(details_table)
    elements.append(Spacer(1, 1*cm))

    try:
        services = ast.literal_eval(invoice_data['services'])
        if not isinstance(services, list):
            services = [("Error parsing services", 0.0)]
    except (ValueError, SyntaxError):
        services = [("Error: Service data is corrupt.", 0.0)]

    data = [["SERVICE DESCRIPTION", "PRICE"]]
    for service, price in services:
        data.append([Paragraph(service, styles['Normal']), f"${price:,.2f}"])
    
    services_table = Table(data, colWidths=[14*cm, 3.5*cm], repeatRows=1)
    services_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0057A0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,0), 'LEFT'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('TOPPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.lightgrey)
    ]))
    elements.append(services_table)

    total_data = [
        [Paragraph(f"TOTAL:", styles['TotalLabel']), Paragraph(f"${invoice_data['total']:,.2f}", styles['TotalValue'])]
    ]
    total_table = Table(total_data, colWidths=[14*cm, 3.5*cm])
    total_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#DEEEF9")),
        ('GRID', (0,0), (-1,-1), 1, colors.lightgrey)
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 1.5*cm))

    payment_terms_data = [
        [Paragraph(settings.get('BANK_DETAILS', ''), styles['Normal']), Paragraph("<b>Terms & Conditions:</b><br/>1. Payment due in 7 days.<br/>2. Late payments may incur fees.<br/>3. All transactions are final.", styles['Normal'])]
    ]
    payment_terms_table = Table(payment_terms_data, colWidths=[8.5*cm, 9*cm])
    payment_terms_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(payment_terms_table)
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph("Thank you for your business!", styles['Italic']))

    def add_watermark(canvas, doc):
        canvas.saveState()
        watermark_text = invoice_data['status'].upper()
        color = colors.green if invoice_data['status'] == 'paid' else colors.red
        canvas.setFont("Helvetica-Bold", 100)
        canvas.setFillColor(color, alpha=0.1)
        canvas.translate(A4[0]/2, A4[1]/2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, watermark_text)
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)
    return filename

# ---------- EMAIL UTILITY ----------
@with_loading("Sending email...")
def send_invoice_email(invoice_data, settings, recipient_email):
    """Sends an invoice PDF via email."""
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not all([settings.get("SMTP_SERVER"), settings.get("SMTP_PORT"), settings.get("SMTP_USERNAME"), smtp_password, settings.get("SMTP_SENDER_EMAIL")]):
        st.error("SMTP settings are not fully configured. Please check Settings and ensure the SMTP_PASSWORD environment variable is set.")
        return False

    pdf_filename = generate_invoice_pdf(invoice_data, settings)

    msg = MIMEMultipart()
    msg['From'] = settings["SMTP_SENDER_EMAIL"]
    msg['To'] = recipient_email
    
    subject_template = settings.get("EMAIL_SUBJECT", "Invoice from {company_name}")
    msg['Subject'] = subject_template.format(company_name=settings.get("COMPANY_NAME", ""))

    body_template = settings.get("EMAIL_BODY", "Please find your invoice attached.")
    body = body_template.format(
        client_name=invoice_data['name'],
        invoice_id=invoice_data['id'],
        total=f"{invoice_data['total']:,.2f}",
        company_name=settings.get("COMPANY_NAME", "")
    )
    msg.attach(MIMEText(body, 'html'))

    with open(pdf_filename, "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename=str(pdf_filename))
        msg.attach(attach)

    try:
        with smtplib.SMTP_SSL(settings["SMTP_SERVER"], int(settings["SMTP_PORT"])) as server:
            server.login(settings["SMTP_USERNAME"], smtp_password)
            server.send_message(msg)
        os.remove(pdf_filename) # Clean up the generated PDF
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        os.remove(pdf_filename) # Clean up even if it fails
        return False

# ---------- UI HELPER ----------
def get_time_of_day_greeting():
    """Returns a greeting based on the current time in Harare."""
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

# ---------- STREAMLIT PAGES ----------
def page_dashboard():
    """The main dashboard page with business analytics."""
    greeting = get_time_of_day_greeting()
    st.header(f"{greeting}, {st.session_state.username}! 👋")
    st.markdown("Here's your business overview.")

    with st.spinner('Loading your dashboard...'):
        invoices = fetch_all_invoices_with_client_info()
        expenses = fetch_all_expenses()
        df_invoices = pd.DataFrame(invoices, columns=invoices[0].keys()) if invoices else pd.DataFrame()
        df_expenses = pd.DataFrame(expenses, columns=expenses[0].keys()) if expenses else pd.DataFrame()

        st.markdown("---")
        
        # Key Metrics in Cards
        with st.container():
            st.subheader("Key Financial Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                with st.container(border=True):
                    total_revenue = sum(inv['total'] for inv in invoices if inv['status'] == 'paid')
                    st.metric("Total Revenue 💵", f"${total_revenue:,.2f}")
            with col2:
                 with st.container(border=True):
                    total_expenses = sum(exp['amount'] for exp in expenses)
                    st.metric("Total Expenses 💸", f"${total_expenses:,.2f}")
            with col3:
                 with st.container(border=True):
                    net_profit = total_revenue - total_expenses
                    st.metric("Net Profit 💰", f"${net_profit:,.2f}")
            with col4:
                 with st.container(border=True):
                    outstanding_revenue = sum(inv['total'] for inv in invoices if inv['status'] == 'unpaid')
                    st.metric("Outstanding ⏰", f"${outstanding_revenue:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True) 

        tab1, tab2 = st.tabs(["📊 Financial Overview", "👥 Client & Expense Insights"])

        with tab1:
            with st.container(border=True):
                st.write("##### Monthly Performance")
                if not df_invoices.empty or not df_expenses.empty:
                    if not df_invoices.empty and df_invoices['status'].eq('paid').any():
                        df_paid = df_invoices[df_invoices['status'] == 'paid'].copy()
                        df_paid['date_dt'] = pd.to_datetime(df_paid['date'], format='%d %B %Y')
                        df_paid['month_year'] = df_paid['date_dt'].dt.to_period('M').astype(str)
                        monthly_revenue = df_paid.groupby('month_year')['total'].sum().reset_index().rename(columns={'total': 'Revenue'})
                    else: monthly_revenue = pd.DataFrame(columns=['month_year', 'Revenue'])

                    if not df_expenses.empty:
                        df_expenses['date_dt'] = pd.to_datetime(df_expenses['date'], format='%Y-%m-%d')
                        df_expenses['month_year'] = df_expenses['date_dt'].dt.to_period('M').astype(str)
                        monthly_expenses = df_expenses.groupby('month_year')['amount'].sum().reset_index().rename(columns={'amount': 'Expenses'})
                    else: monthly_expenses = pd.DataFrame(columns=['month_year', 'Expenses'])

                    df_monthly = pd.merge(monthly_revenue, monthly_expenses, on='month_year', how='outer').fillna(0)
                    df_monthly = pd.melt(df_monthly, id_vars='month_year', value_vars=['Revenue', 'Expenses'], var_name='Metric', value_name='Amount')

                    fig = px.bar(df_monthly, x='month_year', y='Amount', color='Metric', barmode='group', labels={'Amount': 'Amount (USD)', 'month_year': 'Month'}, color_discrete_map={'Revenue': 'green', 'Expenses': 'red'})
                    st.plotly_chart(fig, use_container_width=True)
                else: st.info("No financial data for monthly performance chart.")
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.write("##### Expense Breakdown")
                    if not df_expenses.empty:
                        df_expenses_cat = df_expenses.groupby('category')['amount'].sum().reset_index()
                        fig_exp = px.pie(df_expenses_cat, values='amount', names='category', title='', hole=.3)
                        fig_exp.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_exp, use_container_width=True)
                    else: st.info("No expenses recorded.")
            with col2:
                with st.container(border=True):
                    st.write("##### Invoice Aging (Unpaid)")
                    if not df_invoices.empty:
                        df_unpaid = df_invoices[df_invoices['status'] == 'unpaid'].copy()
                        if not df_unpaid.empty:
                            df_unpaid['date_dt'] = pd.to_datetime(df_unpaid['date'], format='%d %B %Y')
                            today = datetime.datetime.now()
                            df_unpaid['days_overdue'] = (today - df_unpaid['date_dt']).dt.days
                            def age_bucket(days):
                                if days <= 0: return 'Current';
                                if 1 <= days <= 30: return 'Overdue (1-30 Days)';
                                return 'Severely Overdue (30+ Days)'
                            df_unpaid['Aging'] = df_unpaid['days_overdue'].apply(age_bucket)
                            aging_summary = df_unpaid.groupby('Aging')['total'].sum().reset_index()
                            fig_age = px.pie(aging_summary, values='total', names='Aging', color_discrete_map={'Current': 'blue', 'Overdue (1-30 Days)': 'orange', 'Severely Overdue (30+ Days)': 'crimson'})
                            st.plotly_chart(fig_age, use_container_width=True)
                        else: st.info("No unpaid invoices to analyze.")
                    else: st.info("No invoice data available.")

def page_create_invoice():
    """Page for creating a new invoice."""
    st.header("📝 Create New Invoice")
    with st.spinner('Loading client data...'):
        settings = fetch_settings()
        clients = fetch_all_clients()
        projects = fetch_all_projects_with_client_info()
    client_names = [client['name'] for client in clients]
    
    st.subheader("Services")
    if 'services' not in st.session_state: st.session_state.services = [{"service": "", "price": 0.0}]
    for i, item in enumerate(st.session_state.services):
        col1, col2, col3 = st.columns([4, 2, 1])
        st.session_state.services[i]['service'] = col1.text_input(f"Service {i+1}", sanitize_input(item['service']), key=f"service_{i}")
        st.session_state.services[i]['price'] = col2.number_input(f"Price {i+1}", value=item['price'], min_value=0.0, step=10.0, key=f"price_{i}")
        if col3.button("🗑️", key=f"del_{i}"): st.session_state.services.pop(i); st.rerun()
    if st.button("➕ Add Service"): st.session_state.services.append({"service": "", "price": 0.0}); st.rerun()
    total = sum(item['price'] for item in st.session_state.services)
    st.markdown(f"### Total Amount: `${total:,.2f}`")

    with st.form("create_invoice_form"):
        st.subheader("Client & Project Information")
        col1, col2 = st.columns(2)
        selected_client_name = col1.selectbox("Select Client", ["--- New Client ---"] + client_names)
        
        if selected_client_name == "--- New Client ---":
            client_name_input = st.text_input("Client Name*", key="new_client_name")
            client_email_input = st.text_input("Client Email", key="new_client_email")
            client_phone_input = st.text_input("Client Phone", key="new_client_phone")
            selected_client = None
            project_id = None
            col2.info("Save invoice to create projects for this new client.")
        else:
            selected_client = next(c for c in clients if c['name'] == selected_client_name)
            client_name_input = st.text_input("Client Name", selected_client['name'], disabled=True)
            client_email_input = st.text_input("Client Email", selected_client['email'], disabled=True)
            client_phone_input = st.text_input("Client Phone", selected_client['phone'], disabled=True)
            client_projects = [p for p in projects if p['client_id'] == selected_client['id']]
            project_name = col2.selectbox("Link to Project (Optional)", ["None"] + [p['name'] for p in client_projects])
            project_id = next((p['id'] for p in client_projects if p['name'] == project_name), None)
        
        submitted = st.form_submit_button("Generate Invoice", type="primary")

    if submitted:
        # Input validation
        client_name = sanitize_input(client_name_input)
        client_email = sanitize_input(client_email_input)
        client_phone = sanitize_input(client_phone_input)
        
        if not client_name: 
            st.error("Client Name is required.")
            return
            
        if client_email and not validate_email(client_email):
            st.error("Please enter a valid email address.")
            return
            
        if client_phone and not validate_phone(client_phone):
            st.error("Please enter a valid phone number.")
            return
            
        final_services = [(sanitize_input(item['service']), item['price']) for item in st.session_state.services if item['service'].strip() and item['price'] > 0]
        if not final_services: 
            st.error("Add at least one service.")
            return

        with get_db_connection() as conn:
            client_id = selected_client['id'] if selected_client else str(uuid.uuid4())[:8].upper()
            created_at = datetime.datetime.now().isoformat()
            
            if not selected_client: 
                conn.execute('INSERT INTO clients (id, name, email, phone, created_at) VALUES (?, ?, ?, ?, ?)', 
                           (client_id, client_name, client_email, client_phone, created_at))
            
            invoice_id = f"ST-{str(uuid.uuid4())[:6].upper()}"
            invoice_date = datetime.date.today().strftime('%d %B %Y')
            
            conn.execute('INSERT INTO invoices (id, client_id, project_id, services, total, date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                       (invoice_id, client_id, project_id, str(final_services), total, invoice_date, created_at))
            conn.commit()
            
        st.success(f"Invoice {invoice_id} created!")
        
        pdf_data = {'id': invoice_id, 'date': invoice_date, 'total': total, 'status': 'unpaid', 'services': str(final_services), 'name': client_name, 'email': client_email, 'phone': client_phone}
        pdf_file = generate_invoice_pdf(pdf_data, settings)
        with open(pdf_file, "rb") as file: 
            st.download_button("📄 Download PDF", file, pdf_file, "application/pdf")
        if 'services' in st.session_state: 
            del st.session_state.services

def page_invoice_dashboard():
    """Page for viewing, managing, and regenerating invoices."""
    st.header("📊 Invoice Management")
    with st.spinner('Loading invoices...'):
        settings = fetch_settings()
        invoices = fetch_all_invoices_with_client_info()
    if not invoices: st.info("No invoices found."); return

    st.subheader("Filters"); col1, col2 = st.columns(2)
    search_query = st.text_input("Search Client or Invoice ID")
    status_filter = st.selectbox("Filter Status", ["All", "Paid", "Unpaid", "Partially Paid"])
    filtered_invoices = [inv for inv in invoices if (search_query.lower() in inv['name'].lower() or search_query.lower() in inv['id'].lower()) and (status_filter.lower() == 'all' or inv['status'] == status_filter.lower().replace(' ', '_'))]
    if not filtered_invoices: st.warning("No invoices match criteria."); return
        
    for inv in filtered_invoices:
        status_emoji = "🟢" if inv['status'] == 'paid' else "🟡" if inv['status'] == 'partially_paid' else "🔴"
        with st.expander(f"{status_emoji} **{inv['id']}** - {inv['name']} - `${inv['total']:,.2f}`"):
            st.write(f"**Client:** {inv['name']} | **Email:** {inv['email']} | **Phone:** {inv['phone']}")
            try:
                services = ast.literal_eval(inv['services'])
            except (ValueError, SyntaxError):
                services = [("Error parsing services.", "")]
            st.write("**Services:**")
            for service, price in services: st.markdown(f"- {service}: `${price:,.2f}`")
            st.markdown(f"**Total:** `${inv['total']:,.2f}` | **Status:** `{inv['status'].upper().replace('_', ' ')}`")
            
            # Show payment history if any
            payments = fetch_payments_for_invoice(inv['id'])
            if payments:
                st.subheader("Payment History")
                for payment in payments:
                    st.write(f"- ${payment['amount']:,.2f} on {payment['date']} via {payment['method']}")
            
            btn_pdf, btn_mark, btn_delete, btn_payment, btn_share, btn_email = st.columns(6)
            pdf_file = generate_invoice_pdf(inv, settings)
            with open(pdf_file, "rb") as file: 
                btn_pdf.download_button("📄 PDF", file, pdf_file, "application/pdf", key=f"pdf_{inv['id']}")
            
            with get_db_connection() as conn:
                if inv['status'] == 'unpaid':
                    if btn_mark.button("Mark Paid", key=f"paid_{inv['id']}", type="primary"): 
                        conn.execute("UPDATE invoices SET status='paid' WHERE id=?", (inv['id'],)); conn.commit(); st.rerun()
                else:
                    if btn_mark.button("Mark Unpaid", key=f"unpaid_{inv['id']}"): 
                        conn.execute("UPDATE invoices SET status='unpaid' WHERE id=?", (inv['id'],)); conn.commit(); st.rerun()
                
                if btn_delete.button("🗑️ Delete", key=f"del_inv_{inv['id']}"): 
                    conn.execute("DELETE FROM invoices WHERE id=?", (inv['id'],)); conn.commit(); st.rerun()
                
                if btn_payment.button("💰 Record Payment", key=f"pay_{inv['id']}"):
                    with st.form(key=f"payment_form_{inv['id']}"):
                        st.subheader("Record Payment")
                        amount = st.number_input("Amount", min_value=0.0, max_value=float(inv['total']), key=f"amount_{inv['id']}")
                        payment_date = st.date_input("Payment Date", datetime.date.today(), key=f"pdate_{inv['id']}")
                        method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Ecocash", "Innbucks", "Omari", "Other"], key=f"method_{inv['id']}")
                        notes = st.text_input("Notes (Optional)", key=f"notes_{inv['id']}")
                        if st.form_submit_button("Record Payment"):
                            record_payment(inv['id'], amount, payment_date.strftime('%Y-%m-%d'), method, notes)
                            st.success("Payment recorded!")
                            st.rerun()
                
                if btn_share.button("🔗 Share", key=f"share_{inv['id']}"):
                    token = secrets.token_urlsafe(16)
                    expiry = (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
                    created_at = datetime.datetime.now().isoformat()
                    conn.execute("INSERT INTO shared_invoices (id, invoice_id, access_token, expiry_date, created_at) VALUES (?, ?, ?, ?, ?)", 
                               (str(uuid.uuid4()), inv['id'], token, expiry, created_at))
                    conn.commit()
                    share_link = f"{st.get_option('server.baseUrlPath')}?invoice_id={inv['id']}&token={token}"
                    st.code(share_link, language="bash", line_numbers=False); st.info("Link is valid for 30 days. Click the icon above to copy.")
                
                if btn_email.button("📧 Send Email", key=f"email_{inv['id']}"):
                    if inv['email']:
                        if send_invoice_email(inv, settings, inv['email']):
                            st.success(f"Invoice sent to {inv['email']}")
                    else:
                        st.warning("This client does not have an email address on file.")

def page_manage_projects():
    """Page for managing projects."""
    st.header("🛠️ Project Management")
    with st.spinner('Loading projects...'):
        clients = fetch_all_clients()
    PROJECT_STATUSES = ["Not Started", "In Progress", "On Hold", "Completed", "Cancelled"]

    # Check if there are clients first
    if not clients:
        st.warning("You must add a client before you can create a project.")
        st.info("Please add a client first from the 'Manage Clients' page.")
        st.stop()
    
    with st.form("project_form"):
        st.subheader("Add New Project")
        
        col1, col2 = st.columns(2)
        client_id = col1.selectbox("Assign to Client", options=[c['id'] for c in clients], format_func=lambda x: next(c['name'] for c in clients if c['id'] == x))
        name = col1.text_input("Project Name")
        budget = col2.number_input("Budget (USD)", min_value=0.0, step=100.0)
        status = col2.selectbox("Status", PROJECT_STATUSES)
        description = st.text_area("Description")
        
        # Add the missing submit button here
        submitted = st.form_submit_button("Add Project", type="primary")
        
        if submitted:
            if name:
                with get_db_connection() as conn:
                    created_at = datetime.datetime.now().isoformat()
                    conn.execute("INSERT INTO projects (id, client_id, name, budget, status, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                               (str(uuid.uuid4())[:8], client_id, sanitize_input(name), budget, status, sanitize_input(description), created_at))
                    conn.commit()
                st.success("Project added!")
                st.rerun()
            else:
                st.error("Project Name is required.")
    
    st.markdown("---")
    st.subheader("Existing Projects")
    projects = fetch_all_projects_with_client_info()
    if not projects:
        st.info("No projects found.")
        return

    for proj in projects:
        with st.expander(f"**{proj['name']}** ({proj['client_name']}) - Status: `{proj['status']}`"):
            with st.form(key=f"edit_proj_{proj['id']}"):
                st.write(f"**Budget:** ${proj['budget']:,.2f}")
                st.write(f"**Description:** {proj['description']}")
                st.markdown("---")
                st.subheader("Edit Project")
                name = st.text_input("Project Name", value=proj['name'], key=f"name_{proj['id']}")
                budget = st.number_input("Budget (USD)", value=proj['budget'], min_value=0.0, step=100.0, key=f"budget_{proj['id']}")
                status = st.selectbox("Status", PROJECT_STATUSES, index=PROJECT_STATUSES.index(proj['status']), key=f"status_{proj['id']}")
                description = st.text_area("Description", value=proj['description'], key=f"desc_{proj['id']}")
                
                submitted_edit = st.form_submit_button("Update Project", type="primary")
                if submitted_edit:
                    with get_db_connection() as conn:
                        conn.execute("UPDATE projects SET name=?, budget=?, status=?, description=? WHERE id=?", 
                                   (sanitize_input(name), budget, status, sanitize_input(description), proj['id']))
                        conn.commit()
                    st.rerun()
            
            # Delete button outside the form
            st.error("Danger Zone")
            if st.checkbox("Confirm deletion of this project?", key=f"del_check_{proj['id']}"):
                if st.button("🗑️ Delete Project Permanently", key=f"del_btn_{proj['id']}"):
                    with get_db_connection() as conn:
                        conn.execute("DELETE FROM projects WHERE id=?", (proj['id'],))
                        conn.commit()
                    st.rerun()

def page_manage_clients():
    """Page for managing client profiles."""
    st.header("👥 Manage Clients")
    with st.spinner('Loading clients...'):
        clients = fetch_all_clients()

    with st.expander("➕ Add New Client", expanded=not clients):
        with st.form("new_client_form"):
            name = st.text_input("Client Name*")
            email = st.text_input("Client Email")
            phone = st.text_input("Client Phone")
            if st.form_submit_button("Add Client", type="primary"):
                if not name:
                    st.error("Client Name is required.")
                elif email and not validate_email(email):
                    st.error("Please enter a valid email address.")
                elif phone and not validate_phone(phone):
                    st.error("Please enter a valid phone number.")
                else:
                    with get_db_connection() as conn:
                        created_at = datetime.datetime.now().isoformat()
                        conn.execute('INSERT INTO clients (id, name, email, phone, created_at) VALUES (?, ?, ?, ?, ?)', 
                                   (str(uuid.uuid4())[:8].upper(), sanitize_input(name), sanitize_input(email), sanitize_input(phone), created_at))
                        conn.commit()
                    st.success(f"Client '{name}' added successfully.")
                    st.rerun()

    st.subheader("Existing Clients")
    if not clients: st.info("No clients found."); return

    df = pd.DataFrame(clients, columns=clients[0].keys()) if clients else pd.DataFrame()
    st.dataframe(df.drop('id', axis=1), use_container_width=True, hide_index=True)
    st.dataframe(df[['name', 'email', 'phone', 'created_at']], use_container_width=True, hide_index=True)
    st.subheader("Manage Selected Client")
    
    if clients:
        selected_client_id = st.selectbox("Select Client", options=[c['id'] for c in clients], format_func=lambda x: next(c['name'] for c in clients if c['id'] == x))
        if selected_client_id:
            selected_client = next(c for c in clients if c['id'] == selected_client_id)
            with st.form(key=f"edit_client_{selected_client_id}"):
                st.markdown(f"#### Edit: **{selected_client['name']}**")
                name = st.text_input("Name", selected_client['name'])
                email = st.text_input("Email", selected_client['email'])
                phone = st.text_input("Phone", selected_client['phone'])
                if st.form_submit_button("Update Details", type="primary"):
                    # Validate inputs
                    if email and not validate_email(email):
                        st.error("Please enter a valid email address")
                    elif phone and not validate_phone(phone):
                        st.error("Please enter a valid phone number")
                    else:
                        with get_db_connection() as conn:
                            conn.execute('UPDATE clients SET name=?, email=?, phone=? WHERE id=?', 
                                       (sanitize_input(name), sanitize_input(email), sanitize_input(phone), selected_client_id))
                            conn.commit()
                        st.rerun()

            with st.form(key=f"delete_client_{selected_client_id}"):
                st.error(f"**Danger Zone:** Delete Client")
                st.warning(f"This deletes **{selected_client['name']}** and **all associated projects and invoices**.")
                if st.checkbox("Confirm permanent deletion."):
                    if st.form_submit_button("Delete Permanently"):
                        with get_db_connection() as conn:
                            conn.execute('DELETE FROM invoices WHERE client_id=?', (selected_client_id,))
                            conn.execute('DELETE FROM projects WHERE client_id=?', (selected_client_id,))
                            conn.execute('DELETE FROM clients WHERE id=?', (selected_client_id,))
                            conn.commit()
                        st.rerun()

def page_manage_expenses():
    """Page for managing business expenses."""
    st.header("💸 Expense Management")
    EXPENSE_CATEGORIES = ["Software/Tools", "Marketing", "Office Supplies", "Utilities", "Travel", "Rent", "Salaries", "Other"]
    with st.form("expense_form"):
        st.subheader("Add New Expense")
        col1, col2 = st.columns(2)
        date = col1.date_input("Date", datetime.date.today())
        category = col1.selectbox("Category", EXPENSE_CATEGORIES)
        amount = col2.number_input("Amount (USD)", value=0.0, min_value=0.0, step=10.0)
        description = st.text_area("Description")
        if st.form_submit_button("Add Expense"):
            if amount > 0 and description:
                with get_db_connection() as conn:
                    created_at = datetime.datetime.now().isoformat()
                    conn.execute("INSERT INTO expenses (id, date, category, description, amount, created_at) VALUES (?, ?, ?, ?, ?, ?)", 
                               (str(uuid.uuid4())[:8], date.strftime('%Y-%m-%d'), category, sanitize_input(description), amount, created_at))
                    conn.commit()
                st.rerun()
            else: st.error("Amount and description required.")
    st.subheader("Recorded Expenses")
    expenses = fetch_all_expenses()
    if expenses: 
        st.dataframe(pd.DataFrame(expenses, columns=expenses[0].keys()).drop('id', axis=1), use_container_width=True, hide_index=True)
    else: 
        st.info("No expenses recorded yet.")

def page_reports():
    """Page for generating and downloading reports."""
    st.header("📄 Reports")
    with st.spinner('Generating reports...'):
        tab1, tab2, tab3, tab4 = st.tabs(["Financial Reports", "Project Reports", "Client Reports", "Backup & Export"])

        with tab1:
            st.subheader("Generate Financial Reports")
            today = datetime.date.today()
            one_month_ago = today - datetime.timedelta(days=30)
            col1, col2 = st.columns(2)
            start_date = col1.date_input("Start Date", one_month_ago)
            end_date = col2.date_input("End Date", today)
            if start_date and end_date and start_date <= end_date:
                invoices = fetch_all_invoices_with_client_info()
                expenses = fetch_all_expenses()
                df_invoices = pd.DataFrame(invoices, columns=invoices[0].keys()) if invoices else pd.DataFrame()
                if not df_invoices.empty:
                    df_invoices['date_dt'] = pd.to_datetime(df_invoices['date'], format='%d %B %Y').dt.date
                    mask = (df_invoices['date_dt'] >= start_date) & (df_invoices['date_dt'] <= end_date)
                    filtered_invoices = df_invoices.loc[mask]
                    st.write(f"Invoice Report ({start_date} to {end_date})")
                    st.dataframe(filtered_invoices[['id', 'name', 'date', 'total', 'status']], hide_index=True)
                    st.download_button("Download CSV", filtered_invoices.to_csv(index=False).encode('utf-8'), f"invoice_report.csv", "text/csv", key="invoices_csv")
                df_expenses = pd.DataFrame(expenses, columns=expenses[0].keys()) if expenses else pd.DataFrame()
                if not df_expenses.empty:
                    df_expenses['date_dt'] = pd.to_datetime(df_expenses['date']).dt.date
                    mask = (df_expenses['date_dt'] >= start_date) & (df_expenses['date_dt'] <= end_date)
                    filtered_expenses = df_expenses.loc[mask]
                    st.write(f"Expense Report ({start_date} to {end_date})")
                    st.dataframe(filtered_expenses[['date', 'category', 'description', 'amount']], hide_index=True)
                    st.download_button("Download CSV", filtered_expenses.to_csv(index=False).encode('utf-8'), f"expense_report.csv", "text/csv", key="expenses_csv")
        
        with tab2:
            st.subheader("Project Profitability")
            projects = fetch_all_projects_with_client_info()
            invoices = fetch_all_invoices_with_client_info()
            if projects and invoices:
                df_projects = pd.DataFrame(projects, columns=projects[0].keys()) if projects else pd.DataFrame()
                df_invoices = pd.DataFrame(invoices, columns=invoices[0].keys()) if invoices else pd.DataFrame()
                project_revenue = df_invoices[df_invoices['status']=='paid'].groupby('project_id')['total'].sum().reset_index().rename(columns={'total': 'revenue'})
                if not project_revenue.empty:
                    merged = pd.merge(df_projects, project_revenue, left_on='id', right_on='project_id', how='left').fillna(0)
                    merged['profit'] = merged['revenue'] - merged['budget']
                    merged = merged[merged['status'] == 'Completed']
                    fig = px.bar(merged, x='name', y=['revenue', 'budget'], barmode='group', labels={'value': 'Amount (USD)', 'name': 'Project'}, title="Project Revenue vs. Budget")
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(merged[['name', 'client_name', 'budget', 'revenue', 'profit']], hide_index=True)
                else: st.info("No paid invoices linked to completed projects.")
            else: st.info("Create projects and link paid invoices to see profitability.")

        with tab3:
            st.subheader("Client Lifetime Value (LTV)")
            invoices = fetch_all_invoices_with_client_info()
            if invoices:
                df_invoices = pd.DataFrame(invoices, columns=invoices[0].keys()) if invoices else pd.DataFrame()
                client_ltv = df_invoices[df_invoices['status'] == 'paid'].groupby('name')['total'].sum().reset_index().rename(columns={'total': 'Lifetime Value'}).sort_values('Lifetime Value', ascending=False)
                st.dataframe(client_ltv, hide_index=True)
                fig = px.bar(client_ltv, x='name', y='Lifetime Value', title="Total Revenue by Client")
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("No paid invoices to calculate LTV.")

        with tab4:
            st.subheader("Backup & Data Export")
            st.info("Create a backup of your entire database for safekeeping.")
            
            if st.button("Create Database Backup", type="primary"):
                with st.spinner("Creating backup..."):
                    backup_file = export_database_backup()
                    with open(backup_file, "rb") as f:
                        st.download_button(
                            "📥 Download Database Backup",
                            f,
                            file_name=backup_file,
                            mime="application/x-sqlite3"
                        )
                    # Clean up
                    os.remove(backup_file)

def page_settings():
    """Page for updating company and payment information."""
    st.header("⚙️ Application Settings")
    settings = fetch_settings()
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Company & Invoice", "📧 Email (SMTP)", "💰 Tax & Currency", "🔒 Database & Security"])
    
    with tab1:
        with st.form("company_settings_form"):
            st.subheader("Company Information")
            company_name = st.text_input("Company Name", settings.get("COMPANY_NAME", ""))
            company_address = st.text_area("Address", settings.get("COMPANY_ADDRESS", ""))
            company_phone = st.text_input("Phone", settings.get("COMPANY_PHONE", ""))
            company_email = st.text_input("Email", settings.get("COMPANY_EMAIL", ""))
            company_tin = st.text_input("TIN", settings.get("COMPANY_TIN", ""))
            st.subheader("Payment Details")
            bank_details = st.text_area("Payment Details (HTML)", settings.get("BANK_DETAILS", ""), height=150)
            if st.form_submit_button("Save Company Settings", type="primary"):
                updated_settings = {
                    "COMPANY_NAME": sanitize_input(company_name),
                    "COMPANY_ADDRESS": sanitize_input(company_address),
                    "COMPANY_PHONE": sanitize_input(company_phone),
                    "COMPANY_EMAIL": sanitize_input(company_email),
                    "COMPANY_TIN": sanitize_input(company_tin),
                    "BANK_DETAILS": bank_details  # HTML content, don't sanitize
                }
                with get_db_connection() as conn:
                    for key, value in updated_settings.items():
                        conn.execute("UPDATE settings SET value=? WHERE key=?", (value, key))
                    conn.commit()
                st.success("Settings saved!")
                st.rerun()
    

    with tab2:
        with st.form("email_settings_form"):
            st.subheader("SMTP Server Settings")
            st.info("These settings are required to send invoices via email. The SMTP password must be set as an environment variable named `SMTP_PASSWORD` for security.")
            
            smtp_server = st.text_input("SMTP Server", settings.get("SMTP_SERVER", ""))
            smtp_port = st.text_input("SMTP Port", settings.get("SMTP_PORT", "465"))
            smtp_username = st.text_input("SMTP Username", settings.get("SMTP_USERNAME", ""))
            smtp_sender_email = st.text_input("Sender Email Address", settings.get("SMTP_SENDER_EMAIL", ""))
            
            st.subheader("Email Templates")
            email_subject = st.text_input("Email Subject Template", settings.get("EMAIL_SUBJECT", ""))
            email_body = st.text_area("Email Body Template (HTML)", settings.get("EMAIL_BODY", ""), height=200)
            st.caption("Use placeholders: `{company_name}`, `{client_name}`, `{invoice_id}`, `{total}`")

            if st.form_submit_button("Save Email Settings", type="primary"):
                updated_settings = {
                    "SMTP_SERVER": sanitize_input(smtp_server),
                    "SMTP_PORT": sanitize_input(smtp_port),
                    "SMTP_USERNAME": sanitize_input(smtp_username),
                    "SMTP_SENDER_EMAIL": sanitize_input(smtp_sender_email),
                    "EMAIL_SUBJECT": email_subject,
                    "EMAIL_BODY": email_body
                }
                with get_db_connection() as conn:
                    for key, value in updated_settings.items():
                        conn.execute("UPDATE settings SET value=? WHERE key=?", (value, key))
                    conn.commit()
                st.success("Email settings saved!")
                st.rerun()
    
    with tab3:
        st.subheader("Tax Configuration")
        if USE_ENHANCED_FEATURES:
            with st.form("tax_settings_form"):
                tax_enabled = st.checkbox("Enable Tax Calculation", value=settings.get("TAX_ENABLED", "false") == "true")
                tax_type = st.selectbox("Tax Type", ["VAT", "GST", "Sales Tax", "Other"], 
                                       index=["VAT", "GST", "Sales Tax", "Other"].index(settings.get("TAX_TYPE", "VAT")))
                tax_rate = st.number_input("Tax Rate (%)", value=float(settings.get("TAX_RATE", "15")), min_value=0.0, max_value=100.0, step=0.1)
                tax_number = st.text_input("Tax Registration Number", settings.get("TAX_NUMBER", ""))
                
                if st.form_submit_button("Save Tax Settings", type="primary"):
                    with get_db_connection() as conn:
                        conn.execute("UPDATE settings SET value=? WHERE key=?", ("true" if tax_enabled else "false", "TAX_ENABLED"))
                        conn.execute("UPDATE settings SET value=? WHERE key=?", (tax_type, "TAX_TYPE"))
                        conn.execute("UPDATE settings SET value=? WHERE key=?", (str(tax_rate), "TAX_RATE"))
                        conn.execute("UPDATE settings SET value=? WHERE key=?", (tax_number, "TAX_NUMBER"))
                        conn.commit()
                    st.success("Tax settings saved!")
                    st.rerun()
        else:
            st.info("Enhanced tax features require additional modules. Install dependencies to enable.")
        
        st.markdown("---")
        st.subheader("Currency Configuration")
        st.info("Default currency for invoices: USD. Multi-currency support available with enhanced features.")

    with tab4:
        st.subheader("Database Configuration")
        
        # Show current database info
        if USE_ENHANCED_FEATURES:
            db_type = get_db_type()
            st.info(f"**Current Database:** {db_type.upper()}")
            
            # Database health check
            if st.button("Check Database Health"):
                health, message = check_database_health()
                if health:
                    st.success(message)
                else:
                    st.error(message)
            
            st.markdown("---")
            st.subheader("Database Configuration Guide")
            st.markdown("""
            Configure your database using environment variables:
            
            **SQLite (Default):**
            ```bash
            DB_TYPE=sqlite
            DB_NAME=invoices.db
            ```
            
            **PostgreSQL:**
            ```bash
            DB_TYPE=postgresql
            DB_HOST=localhost
            DB_PORT=5432
            DB_USER=your_user
            DB_PASSWORD=your_password
            DB_DATABASE=invoice_db
            ```
            
            **MySQL:**
            ```bash
            DB_TYPE=mysql
            DB_HOST=localhost
            DB_PORT=3306
            DB_USER=your_user
            DB_PASSWORD=your_password
            DB_DATABASE=invoice_db
            ```
            """)
        else:
            st.info("Using SQLite database (default). Install enhanced modules for PostgreSQL/MySQL support.")
        
        st.markdown("---")
        st.subheader("Database Backup")
        st.info("Create a backup of your entire database for safekeeping.")
        
        if st.button("Create Database Backup", type="primary"):
            if USE_ENHANCED_FEATURES and not is_sqlite():
                st.warning("Backup is currently only supported for SQLite databases.")
            else:
                with st.spinner("Creating backup..."):
                    backup_file = export_database_backup()
                    with open(backup_file, "rb") as f:
                        st.download_button(
                            "📥 Download Database Backup",
                            f,
                            file_name=backup_file,
                            mime="application/x-sqlite3"
                        )
                    # Clean up
                    os.remove(backup_file)
        
        st.markdown("---")
        st.subheader("Session Management")
        if st.button("Refresh Session"):
            st.session_state.login_time = time.time()
            st.success("Session refreshed!")
        
        st.info(f"Session timeout: {config.SESSION_TIMEOUT // 3600} hours")

# ---------- LOGIN & PUBLIC INVOICE VIEW ----------
def login_page():
    """Displays the login and signup forms."""
    st.header("Login")
    if not check_for_users():
        st.info("Welcome! Please create the first admin account.")
        with st.form("signup_form"):
            st.subheader("Create Admin Account")
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Sign Up"):
                if new_username and new_password:
                    is_valid, message = validate_password(new_password)
                    if not is_valid:
                        st.error(message)
                    elif new_password == confirm_password:
                        with get_db_connection() as conn:
                            created_at = datetime.datetime.now().isoformat()
                            try: 
                                conn.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)", 
                                           (sanitize_input(new_username), hash_password(new_password), created_at))
                                conn.commit()
                                st.success("Account created successfully! Please log in.")
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("Username already exists.")
                    else: 
                        st.error("Passwords do not match.")
                else: 
                    st.error("Username and password are required.")
    else:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                with get_db_connection() as conn:
                    user = conn.execute("SELECT * FROM users WHERE username=?", (sanitize_input(username),)).fetchone()
                if user and verify_password(user['password'], password):
                    st.session_state.authenticated = True
                    st.session_state.username = user['username']
                    st.session_state.login_time = time.time()
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

def display_shared_invoice(invoice_id, token):
    """Displays a read-only view of a shared invoice if the token is valid."""
    with get_db_connection() as conn:
        share_data = conn.execute("SELECT * FROM shared_invoices WHERE invoice_id=? AND access_token=?", (invoice_id, token)).fetchone()
    
    if share_data:
        # Check expiry
        expiry_date = datetime.datetime.fromisoformat(share_data['expiry_date'])
        if datetime.datetime.now() > expiry_date:
            st.error("This share link has expired.")
            return
        
        invoice = fetch_invoice_by_id(invoice_id)
        settings = fetch_settings()
        if invoice:
            st.title(f"Invoice {invoice['id']}")
            st.markdown(f"**From:** {settings.get('COMPANY_NAME')}")
            st.markdown(f"**To:** {invoice['name']}")
            st.markdown(f"**Date:** {invoice['date']} | **Status:** {invoice['status'].upper()}")
            st.markdown("---")
            st.subheader("Services")
            services = ast.literal_eval(invoice['services'])
            for service, price in services: 
                st.markdown(f"- {service}: `${price:,.2f}`")
            st.markdown("---")
            st.header(f"Total: ${invoice['total']:,.2f}")
            pdf_file = generate_invoice_pdf(invoice, settings)
            with open(pdf_file, "rb") as file: 
                st.download_button("📄 Download PDF", file, pdf_file)
        else: 
            st.error("Invoice not found.")
    else:
        st.error("Invalid or expired share link.")

# ---------- MAIN APP LOGIC ----------
def main_app():
    """The main application interface, shown after successful login."""
    # Check session timeout
    if check_session_timeout():
        # Clear session state on timeout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.warning("Your session has expired. Please log in again.")
        st.rerun()
    
    settings = fetch_settings()
    st.sidebar.title(settings.get("COMPANY_NAME", "Invoice System"))
    st.sidebar.header(f"Welcome, {st.session_state.username}")
    
    # Show session timeout warning
    elapsed_time = time.time() - st.session_state.login_time
    remaining_time = config.SESSION_TIMEOUT - elapsed_time
    if remaining_time < 300:  # 5 minutes remaining
        st.sidebar.warning(f"Session expires in {int(remaining_time // 60)} minutes")
    
    st.sidebar.markdown("---")
    
    menu_options = {
        "📈 Dashboard": page_dashboard, 
        "📝 Create Invoice": page_create_invoice, 
        "📊 Invoice Management": page_invoice_dashboard,
        "🛠️ Project Management": page_manage_projects, 
        "💸 Expense Management": page_manage_expenses, 
        "👥 Manage Clients": page_manage_clients,
        "📄 Reports": page_reports, 
        "⚙️ Settings": page_settings
    }
    selection = st.sidebar.radio("Go to", list(menu_options.keys()))
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"): 
        st.session_state.authenticated = False
        st.rerun()
    
    menu_options[selection]()

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="Slyker Tech Invoicing", 
        page_icon="📈", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database and settings
    try:
        init_db()
        check_and_set_default_settings()
    except Exception as e:
        st.error(f"Failed to initialize application: {str(e)}")
        if config.DEBUG:
            st.error(f"Detailed error: {str(e)}")
        return

    query_params = st.query_params
    invoice_id_param = query_params.get("invoice_id")
    token_param = query_params.get("token")

    if invoice_id_param and token_param:
        display_shared_invoice(invoice_id_param, token_param)
    else:
        if 'authenticated' not in st.session_state: 
            st.session_state.authenticated = False
        if st.session_state.authenticated: 
            main_app()
        else: 
            login_page()

if __name__ == "__main__":
    main()