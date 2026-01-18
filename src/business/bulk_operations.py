"""
Bulk Operations Module for Invoice Utility
Provides functionality for bulk operations on invoices, clients, and other entities
"""
import datetime
import uuid
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


class BulkInvoiceOperations:
    """Class for handling bulk invoice operations"""
    
    @staticmethod
    def bulk_create_invoices(conn, invoice_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create multiple invoices in a single transaction
        
        Args:
            conn: Database connection
            invoice_data_list: List of invoice data dictionaries
            
        Returns:
            Dictionary with created invoice IDs and any errors
        """
        created_invoices = []
        errors = []
        
        for idx, invoice_data in enumerate(invoice_data_list):
            try:
                invoice_id = str(uuid.uuid4())[:8]
                created_at = datetime.datetime.now().isoformat()
                
                # Validate required fields
                required_fields = ['client_id', 'services', 'amounts']
                for field in required_fields:
                    if field not in invoice_data:
                        raise ValueError(f"Missing required field: {field}")
                
                # Calculate totals
                services = invoice_data['services']
                amounts = invoice_data['amounts']
                subtotal = sum(amounts)
                
                # Handle tax if provided
                tax_rate = invoice_data.get('tax_rate', 0)
                tax_amount = subtotal * (tax_rate / 100)
                total = subtotal + tax_amount
                
                # Get optional fields
                project_id = invoice_data.get('project_id')
                currency = invoice_data.get('currency', 'USD')
                due_date = invoice_data.get('due_date')
                notes = invoice_data.get('notes', '')
                
                # Insert invoice
                conn.execute(
                    """INSERT INTO invoices 
                       (id, client_id, services, amounts, total, status, created_at, 
                        project_id, currency, tax_rate, tax_amount, due_date, notes)
                       VALUES (?, ?, ?, ?, ?, 'unpaid', ?, ?, ?, ?, ?, ?, ?)""",
                    (invoice_id, invoice_data['client_id'], str(services), str(amounts),
                     total, created_at, project_id, currency, tax_rate, tax_amount, due_date, notes)
                )
                
                created_invoices.append({
                    'id': invoice_id,
                    'client_id': invoice_data['client_id'],
                    'total': total
                })
                
            except Exception as e:
                errors.append({
                    'index': idx,
                    'data': invoice_data,
                    'error': str(e)
                })
        
        conn.commit()
        
        return {
            'success': True,
            'created_count': len(created_invoices),
            'error_count': len(errors),
            'created_invoices': created_invoices,
            'errors': errors
        }
    
    @staticmethod
    def bulk_update_status(conn, invoice_ids: List[str], new_status: str) -> Dict[str, Any]:
        """
        Update status for multiple invoices
        
        Args:
            conn: Database connection
            invoice_ids: List of invoice IDs
            new_status: New status to set (paid/unpaid/partially_paid)
            
        Returns:
            Dictionary with update results
        """
        updated_count = 0
        errors = []
        
        for invoice_id in invoice_ids:
            try:
                result = conn.execute(
                    "UPDATE invoices SET status = ? WHERE id = ?",
                    (new_status, invoice_id)
                )
                if result.rowcount > 0:
                    updated_count += 1
                else:
                    errors.append({
                        'invoice_id': invoice_id,
                        'error': 'Invoice not found'
                    })
            except Exception as e:
                errors.append({
                    'invoice_id': invoice_id,
                    'error': str(e)
                })
        
        conn.commit()
        
        return {
            'success': True,
            'updated_count': updated_count,
            'error_count': len(errors),
            'errors': errors
        }
    
    @staticmethod
    def bulk_delete_invoices(conn, invoice_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple invoices
        
        Args:
            conn: Database connection
            invoice_ids: List of invoice IDs to delete
            
        Returns:
            Dictionary with deletion results
        """
        deleted_count = 0
        errors = []
        
        for invoice_id in invoice_ids:
            try:
                # Delete associated payments first
                conn.execute("DELETE FROM payments WHERE invoice_id = ?", (invoice_id,))
                
                # Delete invoice
                result = conn.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
                if result.rowcount > 0:
                    deleted_count += 1
                else:
                    errors.append({
                        'invoice_id': invoice_id,
                        'error': 'Invoice not found'
                    })
            except Exception as e:
                errors.append({
                    'invoice_id': invoice_id,
                    'error': str(e)
                })
        
        conn.commit()
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'error_count': len(errors),
            'errors': errors
        }
    
    @staticmethod
    def bulk_send_emails(conn, invoice_ids: List[str], email_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send emails for multiple invoices
        
        Args:
            conn: Database connection
            invoice_ids: List of invoice IDs
            email_settings: Email configuration
            
        Returns:
            Dictionary with email sending results
        """
        sent_count = 0
        errors = []
        
        for invoice_id in invoice_ids:
            try:
                # Get invoice and client details
                invoice = conn.execute(
                    """SELECT i.*, c.email as client_email, c.name as client_name
                       FROM invoices i
                       JOIN clients c ON i.client_id = c.id
                       WHERE i.id = ?""",
                    (invoice_id,)
                ).fetchone()
                
                if not invoice:
                    errors.append({
                        'invoice_id': invoice_id,
                        'error': 'Invoice not found'
                    })
                    continue
                
                if not invoice['client_email']:
                    errors.append({
                        'invoice_id': invoice_id,
                        'error': 'Client email not available'
                    })
                    continue
                
                # Here you would implement actual email sending
                # For now, just mark as success
                sent_count += 1
                
            except Exception as e:
                errors.append({
                    'invoice_id': invoice_id,
                    'error': str(e)
                })
        
        return {
            'success': True,
            'sent_count': sent_count,
            'error_count': len(errors),
            'errors': errors
        }


class BulkClientOperations:
    """Class for handling bulk client operations"""
    
    @staticmethod
    def bulk_import_clients(conn, clients_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Import multiple clients in bulk
        
        Args:
            conn: Database connection
            clients_data: List of client data dictionaries
            
        Returns:
            Dictionary with import results
        """
        imported_count = 0
        errors = []
        
        for idx, client_data in enumerate(clients_data):
            try:
                # Validate required fields
                if 'name' not in client_data:
                    raise ValueError("Missing required field: name")
                
                client_id = str(uuid.uuid4())[:8]
                created_at = datetime.datetime.now().isoformat()
                
                conn.execute(
                    """INSERT INTO clients (id, name, email, phone, created_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (client_id, client_data['name'], 
                     client_data.get('email', ''),
                     client_data.get('phone', ''),
                     created_at)
                )
                
                imported_count += 1
                
            except Exception as e:
                errors.append({
                    'index': idx,
                    'data': client_data,
                    'error': str(e)
                })
        
        conn.commit()
        
        return {
            'success': True,
            'imported_count': imported_count,
            'error_count': len(errors),
            'errors': errors
        }
    
    @staticmethod
    def bulk_update_clients(conn, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update multiple clients
        
        Args:
            conn: Database connection
            updates: List of update dictionaries with 'id' and fields to update
            
        Returns:
            Dictionary with update results
        """
        updated_count = 0
        errors = []
        
        for update_data in updates:
            try:
                client_id = update_data.get('id')
                if not client_id:
                    raise ValueError("Missing client ID")
                
                # Build update query dynamically based on provided fields
                update_fields = []
                params = []
                
                for field in ['name', 'email', 'phone']:
                    if field in update_data:
                        update_fields.append(f"{field} = ?")
                        params.append(update_data[field])
                
                if update_fields:
                    params.append(client_id)
                    query = f"UPDATE clients SET {', '.join(update_fields)} WHERE id = ?"
                    result = conn.execute(query, params)
                    
                    if result.rowcount > 0:
                        updated_count += 1
                    else:
                        errors.append({
                            'client_id': client_id,
                            'error': 'Client not found'
                        })
                
            except Exception as e:
                errors.append({
                    'data': update_data,
                    'error': str(e)
                })
        
        conn.commit()
        
        return {
            'success': True,
            'updated_count': updated_count,
            'error_count': len(errors),
            'errors': errors
        }


class BulkReporting:
    """Class for bulk reporting and data export"""
    
    @staticmethod
    def generate_bulk_report(conn, invoice_ids: List[str]) -> Dict[str, Any]:
        """
        Generate a consolidated report for multiple invoices
        
        Args:
            conn: Database connection
            invoice_ids: List of invoice IDs
            
        Returns:
            Dictionary with aggregated report data
        """
        total_amount = 0
        total_paid = 0
        total_outstanding = 0
        invoice_details = []
        
        for invoice_id in invoice_ids:
            invoice = conn.execute(
                """SELECT i.*, c.name as client_name
                   FROM invoices i
                   JOIN clients c ON i.client_id = c.id
                   WHERE i.id = ?""",
                (invoice_id,)
            ).fetchone()
            
            if invoice:
                total_amount += invoice['total']
                
                # Get paid amount
                payments = conn.execute(
                    "SELECT SUM(amount) as paid FROM payments WHERE invoice_id = ?",
                    (invoice_id,)
                ).fetchone()
                
                paid_amount = payments['paid'] if payments and payments['paid'] else 0
                total_paid += paid_amount
                
                outstanding = invoice['total'] - paid_amount
                total_outstanding += outstanding
                
                invoice_details.append({
                    'id': invoice['id'],
                    'client_name': invoice['client_name'],
                    'total': invoice['total'],
                    'paid': paid_amount,
                    'outstanding': outstanding,
                    'status': invoice['status'],
                    'created_at': invoice['created_at']
                })
        
        return {
            'success': True,
            'total_invoices': len(invoice_details),
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_outstanding': total_outstanding,
            'invoice_details': invoice_details
        }
