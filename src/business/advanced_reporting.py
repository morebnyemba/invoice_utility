"""
Advanced Reporting and Analytics Module
Provides comprehensive reporting capabilities with predictive analytics
"""
import datetime
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
import json


class AdvancedReporting:
    """Advanced reporting and analytics features"""
    
    @staticmethod
    def revenue_trend_analysis(conn, months: int = 12) -> Dict[str, Any]:
        """
        Analyze revenue trends over specified months
        
        Args:
            conn: Database connection
            months: Number of months to analyze
            
        Returns:
            Dictionary with trend analysis data
        """
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=months * 30)
        
        # Get all invoices in date range
        invoices = conn.execute(
            """SELECT created_at, total, status
               FROM invoices
               WHERE created_at >= ?
               ORDER BY created_at""",
            (start_date.isoformat(),)
        ).fetchall()
        
        # Organize by month
        monthly_data = {}
        for invoice in invoices:
            try:
                date = datetime.datetime.fromisoformat(invoice['created_at'])
                month_key = date.strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'revenue': 0,
                        'invoice_count': 0,
                        'paid_count': 0,
                        'unpaid_count': 0
                    }
                
                monthly_data[month_key]['revenue'] += invoice['total']
                monthly_data[month_key]['invoice_count'] += 1
                
                if invoice['status'] == 'paid':
                    monthly_data[month_key]['paid_count'] += 1
                else:
                    monthly_data[month_key]['unpaid_count'] += 1
            except:
                continue
        
        # Calculate trends
        months_list = sorted(monthly_data.keys())
        if len(months_list) >= 2:
            # Calculate month-over-month growth
            latest_month = monthly_data[months_list[-1]]['revenue']
            previous_month = monthly_data[months_list[-2]]['revenue']
            
            if previous_month > 0:
                growth_rate = ((latest_month - previous_month) / previous_month) * 100
            else:
                growth_rate = 0
        else:
            growth_rate = 0
        
        # Calculate average monthly revenue
        total_revenue = sum(month['revenue'] for month in monthly_data.values())
        avg_monthly_revenue = total_revenue / len(monthly_data) if monthly_data else 0
        
        return {
            'success': True,
            'period_months': months,
            'monthly_data': monthly_data,
            'total_revenue': total_revenue,
            'avg_monthly_revenue': avg_monthly_revenue,
            'growth_rate': growth_rate,
            'months_analyzed': len(monthly_data)
        }
    
    @staticmethod
    def expense_breakdown_analysis(conn, start_date: Optional[str] = None, 
                                   end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze expenses by category
        
        Args:
            conn: Database connection
            start_date: Start date for analysis (ISO format)
            end_date: End date for analysis (ISO format)
            
        Returns:
            Dictionary with expense breakdown
        """
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.datetime.now().isoformat()
        if not start_date:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).isoformat()
        
        # Get expenses in date range
        expenses = conn.execute(
            """SELECT category, amount, date, description
               FROM expenses
               WHERE date >= ? AND date <= ?
               ORDER BY date""",
            (start_date, end_date)
        ).fetchall()
        
        # Organize by category
        category_totals = {}
        total_expenses = 0
        
        for expense in expenses:
            category = expense['category'] or 'Uncategorized'
            amount = expense['amount']
            
            if category not in category_totals:
                category_totals[category] = {
                    'total': 0,
                    'count': 0,
                    'avg': 0
                }
            
            category_totals[category]['total'] += amount
            category_totals[category]['count'] += 1
            total_expenses += amount
        
        # Calculate averages and percentages
        for category in category_totals:
            count = category_totals[category]['count']
            total = category_totals[category]['total']
            category_totals[category]['avg'] = total / count if count > 0 else 0
            category_totals[category]['percentage'] = (total / total_expenses * 100) if total_expenses > 0 else 0
        
        return {
            'success': True,
            'start_date': start_date,
            'end_date': end_date,
            'category_breakdown': category_totals,
            'total_expenses': total_expenses,
            'expense_count': len(expenses),
            'categories_count': len(category_totals)
        }
    
    @staticmethod
    def client_performance_metrics(conn, top_n: int = 10) -> Dict[str, Any]:
        """
        Analyze client performance and lifetime value
        
        Args:
            conn: Database connection
            top_n: Number of top clients to return
            
        Returns:
            Dictionary with client performance data
        """
        # Get all clients with their invoice data
        clients = conn.execute(
            """SELECT c.id, c.name, c.email, c.created_at,
                      COUNT(i.id) as invoice_count,
                      SUM(i.total) as total_revenue,
                      AVG(i.total) as avg_invoice_value,
                      MAX(i.created_at) as last_invoice_date
               FROM clients c
               LEFT JOIN invoices i ON c.id = i.client_id
               GROUP BY c.id, c.name, c.email, c.created_at
               ORDER BY total_revenue DESC""",
        ).fetchall()
        
        client_metrics = []
        total_clients = 0
        active_clients = 0
        
        for client in clients:
            if client['invoice_count'] is None or client['invoice_count'] == 0:
                continue
            
            total_clients += 1
            
            # Calculate days since last invoice
            if client['last_invoice_date']:
                try:
                    last_date = datetime.datetime.fromisoformat(client['last_invoice_date'])
                    days_since = (datetime.datetime.now() - last_date).days
                    is_active = days_since < 90  # Active if invoiced in last 90 days
                    if is_active:
                        active_clients += 1
                except:
                    days_since = None
                    is_active = False
            else:
                days_since = None
                is_active = False
            
            # Get payment data
            payments = conn.execute(
                """SELECT SUM(p.amount) as total_paid
                   FROM payments p
                   JOIN invoices i ON p.invoice_id = i.id
                   WHERE i.client_id = ?""",
                (client['id'],)
            ).fetchone()
            
            total_paid = payments['total_paid'] if payments and payments['total_paid'] else 0
            total_revenue = client['total_revenue'] or 0
            outstanding = total_revenue - total_paid
            
            client_metrics.append({
                'id': client['id'],
                'name': client['name'],
                'email': client['email'],
                'invoice_count': client['invoice_count'],
                'total_revenue': total_revenue,
                'total_paid': total_paid,
                'outstanding': outstanding,
                'avg_invoice_value': client['avg_invoice_value'] or 0,
                'last_invoice_date': client['last_invoice_date'],
                'days_since_last_invoice': days_since,
                'is_active': is_active
            })
        
        # Sort by revenue and get top N
        top_clients = sorted(client_metrics, key=lambda x: x['total_revenue'], reverse=True)[:top_n]
        
        return {
            'success': True,
            'total_clients': total_clients,
            'active_clients': active_clients,
            'inactive_clients': total_clients - active_clients,
            'top_clients': top_clients,
            'all_clients': client_metrics
        }
    
    @staticmethod
    def project_profitability_analysis(conn) -> Dict[str, Any]:
        """
        Analyze profitability by project
        
        Args:
            conn: Database connection
            
        Returns:
            Dictionary with project profitability data
        """
        # Get all projects with invoice and expense data
        projects = conn.execute(
            """SELECT p.id, p.name, p.client_id, p.budget, p.status,
                      c.name as client_name
               FROM projects p
               LEFT JOIN clients c ON p.client_id = c.id""",
        ).fetchall()
        
        project_metrics = []
        
        for project in projects:
            # Get project revenue (sum of invoice totals)
            invoices = conn.execute(
                """SELECT SUM(total) as revenue, COUNT(*) as invoice_count
                   FROM invoices
                   WHERE project_id = ?""",
                (project['id'],)
            ).fetchone()
            
            revenue = invoices['revenue'] if invoices and invoices['revenue'] else 0
            invoice_count = invoices['invoice_count'] if invoices else 0
            
            # Get project expenses
            expenses = conn.execute(
                """SELECT SUM(amount) as total_expenses
                   FROM expenses
                   WHERE project_id = ?""",
                (project['id'],)
            ).fetchone()
            
            total_expenses = expenses['total_expenses'] if expenses and expenses['total_expenses'] else 0
            
            # Calculate profitability
            profit = revenue - total_expenses
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0
            budget = project['budget'] or 0
            budget_utilization = (total_expenses / budget * 100) if budget > 0 else 0
            
            project_metrics.append({
                'id': project['id'],
                'name': project['name'],
                'client_name': project['client_name'],
                'status': project['status'],
                'budget': budget,
                'revenue': revenue,
                'expenses': total_expenses,
                'profit': profit,
                'profit_margin': profit_margin,
                'budget_utilization': budget_utilization,
                'invoice_count': invoice_count
            })
        
        # Sort by profit
        sorted_projects = sorted(project_metrics, key=lambda x: x['profit'], reverse=True)
        
        # Calculate totals
        total_revenue = sum(p['revenue'] for p in project_metrics)
        total_expenses = sum(p['expenses'] for p in project_metrics)
        total_profit = total_revenue - total_expenses
        
        return {
            'success': True,
            'total_projects': len(project_metrics),
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'total_profit': total_profit,
            'overall_profit_margin': (total_profit / total_revenue * 100) if total_revenue > 0 else 0,
            'projects': sorted_projects
        }
    
    @staticmethod
    def predictive_analytics(conn) -> Dict[str, Any]:
        """
        Generate predictive analytics for revenue forecasting
        
        Args:
            conn: Database connection
            
        Returns:
            Dictionary with predictive analytics
        """
        # Get last 12 months of data
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=365)
        
        invoices = conn.execute(
            """SELECT created_at, total
               FROM invoices
               WHERE created_at >= ?
               ORDER BY created_at""",
            (start_date.isoformat(),)
        ).fetchall()
        
        if not invoices:
            return {
                'success': True,
                'message': 'Insufficient data for predictions',
                'predicted_next_month': 0,
                'predicted_next_quarter': 0
            }
        
        # Organize by month
        monthly_revenue = {}
        for invoice in invoices:
            try:
                date = datetime.datetime.fromisoformat(invoice['created_at'])
                month_key = date.strftime('%Y-%m')
                
                if month_key not in monthly_revenue:
                    monthly_revenue[month_key] = 0
                
                monthly_revenue[month_key] += invoice['total']
            except:
                continue
        
        # Simple moving average for prediction
        months = sorted(monthly_revenue.keys())
        if len(months) >= 3:
            # Use last 3 months for prediction
            recent_months = months[-3:]
            avg_recent = sum(monthly_revenue[m] for m in recent_months) / 3
            
            # Calculate trend
            if len(months) >= 6:
                older_months = months[-6:-3]
                avg_older = sum(monthly_revenue[m] for m in older_months) / 3
                trend = (avg_recent - avg_older) / avg_older if avg_older > 0 else 0
            else:
                trend = 0
            
            # Predict next month (with trend adjustment)
            predicted_next_month = avg_recent * (1 + trend)
            predicted_next_quarter = predicted_next_month * 3
        else:
            # Not enough data for sophisticated prediction
            avg_all = sum(monthly_revenue.values()) / len(monthly_revenue)
            predicted_next_month = avg_all
            predicted_next_quarter = avg_all * 3
        
        # Calculate confidence based on consistency
        if len(monthly_revenue) >= 3:
            revenues = list(monthly_revenue.values())
            avg = sum(revenues) / len(revenues)
            variance = sum((r - avg) ** 2 for r in revenues) / len(revenues)
            std_dev = variance ** 0.5
            coefficient_of_variation = (std_dev / avg) if avg > 0 else 1
            
            # Lower CV means higher confidence
            confidence = max(0, min(100, (1 - coefficient_of_variation) * 100))
        else:
            confidence = 30  # Low confidence with little data
        
        return {
            'success': True,
            'predicted_next_month': predicted_next_month,
            'predicted_next_quarter': predicted_next_quarter,
            'confidence_score': confidence,
            'months_analyzed': len(monthly_revenue),
            'historical_average': sum(monthly_revenue.values()) / len(monthly_revenue) if monthly_revenue else 0
        }
    
    @staticmethod
    def invoice_aging_report(conn) -> Dict[str, Any]:
        """
        Generate invoice aging report showing overdue invoices
        
        Args:
            conn: Database connection
            
        Returns:
            Dictionary with aging analysis
        """
        current_date = datetime.datetime.now()
        
        # Get all unpaid and partially paid invoices
        invoices = conn.execute(
            """SELECT i.id, i.total, i.created_at, i.due_date, i.status,
                      c.name as client_name
               FROM invoices i
               JOIN clients c ON i.client_id = c.id
               WHERE i.status IN ('unpaid', 'partially_paid')""",
        ).fetchall()
        
        aging_buckets = {
            'current': {'count': 0, 'amount': 0, 'invoices': []},
            '1-30_days': {'count': 0, 'amount': 0, 'invoices': []},
            '31-60_days': {'count': 0, 'amount': 0, 'invoices': []},
            '61-90_days': {'count': 0, 'amount': 0, 'invoices': []},
            'over_90_days': {'count': 0, 'amount': 0, 'invoices': []}
        }
        
        for invoice in invoices:
            # Calculate outstanding amount
            payments = conn.execute(
                "SELECT SUM(amount) as paid FROM payments WHERE invoice_id = ?",
                (invoice['id'],)
            ).fetchone()
            
            paid_amount = payments['paid'] if payments and payments['paid'] else 0
            outstanding = invoice['total'] - paid_amount
            
            # Determine age
            if invoice['due_date']:
                try:
                    due_date = datetime.datetime.fromisoformat(invoice['due_date'])
                    days_overdue = (current_date - due_date).days
                except:
                    days_overdue = 0
            else:
                # Use created date if no due date
                try:
                    created_date = datetime.datetime.fromisoformat(invoice['created_at'])
                    days_overdue = (current_date - created_date).days
                except:
                    days_overdue = 0
            
            # Categorize into bucket
            invoice_data = {
                'id': invoice['id'],
                'client_name': invoice['client_name'],
                'total': invoice['total'],
                'outstanding': outstanding,
                'days_overdue': days_overdue
            }
            
            if days_overdue < 0:
                bucket = 'current'
            elif days_overdue <= 30:
                bucket = '1-30_days'
            elif days_overdue <= 60:
                bucket = '31-60_days'
            elif days_overdue <= 90:
                bucket = '61-90_days'
            else:
                bucket = 'over_90_days'
            
            aging_buckets[bucket]['count'] += 1
            aging_buckets[bucket]['amount'] += outstanding
            aging_buckets[bucket]['invoices'].append(invoice_data)
        
        total_outstanding = sum(bucket['amount'] for bucket in aging_buckets.values())
        
        return {
            'success': True,
            'total_outstanding': total_outstanding,
            'total_invoices': sum(bucket['count'] for bucket in aging_buckets.values()),
            'aging_buckets': aging_buckets
        }
