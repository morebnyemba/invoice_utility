"""
Invoice Scheduler Module
Handles automated recurring invoice generation and scheduling
"""
import datetime
import uuid
from typing import Dict, List, Any, Optional
import threading
import time


class InvoiceScheduler:
    """
    Automated scheduler for recurring invoices
    Generates invoices based on recurring invoice schedules
    """
    
    def __init__(self, db_connection_func):
        """
        Initialize the scheduler
        
        Args:
            db_connection_func: Function that returns a database connection
        """
        self.get_db_connection = db_connection_func
        self.is_running = False
        self.scheduler_thread = None
    
    def start(self, check_interval: int = 3600):
        """
        Start the background scheduler
        
        Args:
            check_interval: How often to check for invoices to generate (seconds)
        """
        if self.is_running:
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler,
            args=(check_interval,),
            daemon=True
        )
        self.scheduler_thread.start()
    
    def stop(self):
        """Stop the background scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def _run_scheduler(self, check_interval: int):
        """
        Background thread that checks for invoices to generate
        
        Args:
            check_interval: Check interval in seconds
        """
        while self.is_running:
            try:
                self.process_recurring_invoices()
            except Exception as e:
                print(f"Error in scheduler: {e}")
            
            # Sleep for the check interval
            time.sleep(check_interval)
    
    def process_recurring_invoices(self) -> Dict[str, Any]:
        """
        Process all recurring invoices that are due
        
        Returns:
            Dictionary with processing results
        """
        generated_invoices = []
        errors = []
        
        with self.get_db_connection() as conn:
            # Get all active recurring invoices
            recurring = conn.execute(
                """SELECT * FROM recurring_invoices 
                   WHERE is_active = 1 AND (end_date IS NULL OR end_date >= ?)""",
                (datetime.datetime.now().isoformat(),)
            ).fetchall()
            
            for rec_invoice in recurring:
                try:
                    # Check if it's time to generate
                    if self._should_generate_invoice(rec_invoice):
                        # Generate the invoice
                        invoice_id = self._generate_from_recurring(conn, rec_invoice)
                        generated_invoices.append({
                            'recurring_id': rec_invoice['id'],
                            'invoice_id': invoice_id
                        })
                        
                        # Update last generated date
                        conn.execute(
                            "UPDATE recurring_invoices SET last_generated = ? WHERE id = ?",
                            (datetime.datetime.now().isoformat(), rec_invoice['id'])
                        )
                        conn.commit()
                
                except Exception as e:
                    errors.append({
                        'recurring_id': rec_invoice['id'],
                        'error': str(e)
                    })
        
        return {
            'success': True,
            'generated_count': len(generated_invoices),
            'error_count': len(errors),
            'generated_invoices': generated_invoices,
            'errors': errors
        }
    
    def _should_generate_invoice(self, recurring_invoice: Dict[str, Any]) -> bool:
        """
        Check if a recurring invoice should generate a new invoice
        
        Args:
            recurring_invoice: Recurring invoice record
            
        Returns:
            True if invoice should be generated
        """
        last_generated = recurring_invoice.get('last_generated')
        frequency = recurring_invoice['frequency']
        
        # If never generated, check start date
        if not last_generated:
            start_date = datetime.datetime.fromisoformat(recurring_invoice['start_date'])
            return datetime.datetime.now() >= start_date
        
        # Calculate next due date based on frequency
        try:
            last_gen_date = datetime.datetime.fromisoformat(last_generated)
        except:
            return True  # If parsing fails, generate to be safe
        
        current_date = datetime.datetime.now()
        
        if frequency == 'weekly':
            next_due = last_gen_date + datetime.timedelta(days=7)
        elif frequency == 'monthly':
            # Add one month (approximate with 30 days)
            next_due = last_gen_date + datetime.timedelta(days=30)
        elif frequency == 'quarterly':
            next_due = last_gen_date + datetime.timedelta(days=90)
        elif frequency == 'yearly':
            next_due = last_gen_date + datetime.timedelta(days=365)
        else:
            return False
        
        return current_date >= next_due
    
    def _generate_from_recurring(self, conn, recurring_invoice: Dict[str, Any]) -> str:
        """
        Generate an invoice from a recurring invoice template
        
        Args:
            conn: Database connection
            recurring_invoice: Recurring invoice record
            
        Returns:
            Generated invoice ID
        """
        import ast
        
        invoice_id = str(uuid.uuid4())[:8]
        created_at = datetime.datetime.now().isoformat()
        
        # Parse services and amounts
        try:
            services = ast.literal_eval(recurring_invoice['services'])
            amounts = ast.literal_eval(recurring_invoice['amounts'])
        except:
            # Fallback if parsing fails
            services = [recurring_invoice['services']]
            amounts = [recurring_invoice['total']]
        
        # Calculate due date based on payment terms
        payment_terms_days = recurring_invoice.get('payment_terms_days', 30)
        due_date = (datetime.datetime.now() + 
                   datetime.timedelta(days=payment_terms_days)).isoformat()
        
        # Insert invoice
        conn.execute(
            """INSERT INTO invoices 
               (id, client_id, services, amounts, total, status, created_at, 
                due_date, currency, notes)
               VALUES (?, ?, ?, ?, ?, 'unpaid', ?, ?, ?, ?)""",
            (invoice_id, recurring_invoice['client_id'], 
             str(services), str(amounts),
             recurring_invoice['total'], created_at,
             due_date, recurring_invoice.get('currency', 'USD'),
             'Auto-generated from recurring invoice')
        )
        
        return invoice_id
    
    def manual_generate(self, recurring_invoice_id: str) -> Dict[str, Any]:
        """
        Manually trigger invoice generation for a recurring invoice
        
        Args:
            recurring_invoice_id: ID of recurring invoice
            
        Returns:
            Dictionary with generation result
        """
        try:
            with self.get_db_connection() as conn:
                # Get recurring invoice
                recurring = conn.execute(
                    "SELECT * FROM recurring_invoices WHERE id = ?",
                    (recurring_invoice_id,)
                ).fetchone()
                
                if not recurring:
                    return {
                        'success': False,
                        'error': 'Recurring invoice not found'
                    }
                
                # Generate invoice
                invoice_id = self._generate_from_recurring(conn, recurring)
                
                # Update last generated
                conn.execute(
                    "UPDATE recurring_invoices SET last_generated = ? WHERE id = ?",
                    (datetime.datetime.now().isoformat(), recurring_invoice_id)
                )
                conn.commit()
                
                return {
                    'success': True,
                    'invoice_id': invoice_id,
                    'message': 'Invoice generated successfully'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_upcoming_invoices(self, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Get list of invoices that will be generated in the next N days
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            Dictionary with upcoming invoices
        """
        upcoming = []
        
        with self.get_db_connection() as conn:
            # Get all active recurring invoices
            recurring = conn.execute(
                """SELECT r.*, c.name as client_name
                   FROM recurring_invoices r
                   JOIN clients c ON r.client_id = c.id
                   WHERE r.is_active = 1""",
            ).fetchall()
            
            end_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
            
            for rec_invoice in recurring:
                # Calculate next generation date
                last_generated = rec_invoice.get('last_generated')
                frequency = rec_invoice['frequency']
                
                if not last_generated:
                    next_date = datetime.datetime.fromisoformat(rec_invoice['start_date'])
                else:
                    try:
                        last_gen_date = datetime.datetime.fromisoformat(last_generated)
                    except:
                        continue
                    
                    if frequency == 'weekly':
                        next_date = last_gen_date + datetime.timedelta(days=7)
                    elif frequency == 'monthly':
                        next_date = last_gen_date + datetime.timedelta(days=30)
                    elif frequency == 'quarterly':
                        next_date = last_gen_date + datetime.timedelta(days=90)
                    elif frequency == 'yearly':
                        next_date = last_gen_date + datetime.timedelta(days=365)
                    else:
                        continue
                
                # Check if within range
                if datetime.datetime.now() <= next_date <= end_date:
                    upcoming.append({
                        'recurring_id': rec_invoice['id'],
                        'client_name': rec_invoice['client_name'],
                        'amount': rec_invoice['total'],
                        'frequency': frequency,
                        'next_generation_date': next_date.isoformat(),
                        'days_until': (next_date - datetime.datetime.now()).days
                    })
        
        # Sort by next generation date
        upcoming.sort(key=lambda x: x['next_generation_date'])
        
        return {
            'success': True,
            'upcoming_invoices': upcoming,
            'count': len(upcoming)
        }


class NotificationManager:
    """
    Manages email and other notifications for automated invoices
    """
    
    def __init__(self, db_connection_func):
        """
        Initialize notification manager
        
        Args:
            db_connection_func: Function that returns a database connection
        """
        self.get_db_connection = db_connection_func
    
    def send_invoice_notification(self, invoice_id: str, notification_type: str = 'created') -> Dict[str, Any]:
        """
        Send notification for an invoice
        
        Args:
            invoice_id: Invoice ID
            notification_type: Type of notification (created, reminder, overdue)
            
        Returns:
            Dictionary with send result
        """
        try:
            with self.get_db_connection() as conn:
                # Get invoice and client details
                invoice = conn.execute(
                    """SELECT i.*, c.email as client_email, c.name as client_name
                       FROM invoices i
                       JOIN clients c ON i.client_id = c.id
                       WHERE i.id = ?""",
                    (invoice_id,)
                ).fetchone()
                
                if not invoice:
                    return {
                        'success': False,
                        'error': 'Invoice not found'
                    }
                
                if not invoice['client_email']:
                    return {
                        'success': False,
                        'error': 'Client email not available'
                    }
                
                # Here you would implement actual email sending
                # For now, just log the notification
                notification_log = {
                    'invoice_id': invoice_id,
                    'client_email': invoice['client_email'],
                    'type': notification_type,
                    'sent_at': datetime.datetime.now().isoformat()
                }
                
                # Store notification in audit log
                conn.execute(
                    """INSERT INTO audit_logs (id, user, action, entity, entity_id, timestamp, details)
                       VALUES (?, 'system', 'notification_sent', 'invoice', ?, ?, ?)""",
                    (str(uuid.uuid4())[:8], invoice_id, 
                     datetime.datetime.now().isoformat(),
                     str(notification_log))
                )
                conn.commit()
                
                return {
                    'success': True,
                    'message': f'Notification sent to {invoice["client_email"]}',
                    'notification_type': notification_type
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_batch_reminders(self, days_overdue: int = 7) -> Dict[str, Any]:
        """
        Send reminders for overdue invoices
        
        Args:
            days_overdue: Minimum days overdue to send reminder
            
        Returns:
            Dictionary with batch send results
        """
        sent_count = 0
        errors = []
        
        with self.get_db_connection() as conn:
            # Get overdue invoices
            cutoff_date = (datetime.datetime.now() - 
                          datetime.timedelta(days=days_overdue)).isoformat()
            
            invoices = conn.execute(
                """SELECT i.id, i.due_date
                   FROM invoices i
                   WHERE i.status IN ('unpaid', 'partially_paid')
                   AND i.due_date < ?""",
                (cutoff_date,)
            ).fetchall()
            
            for invoice in invoices:
                result = self.send_invoice_notification(invoice['id'], 'reminder')
                if result['success']:
                    sent_count += 1
                else:
                    errors.append({
                        'invoice_id': invoice['id'],
                        'error': result.get('error')
                    })
        
        return {
            'success': True,
            'sent_count': sent_count,
            'error_count': len(errors),
            'errors': errors
        }
