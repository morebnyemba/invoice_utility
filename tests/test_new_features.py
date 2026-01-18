#!/usr/bin/env python3
"""
Test script for new features
"""
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_bulk_operations():
    """Test bulk operations module"""
    print("Testing bulk operations...")
    try:
        from src.business.bulk_operations import (
            BulkInvoiceOperations,
            BulkClientOperations,
            BulkReporting
        )
        print("✓ Bulk operations module imported")
        
        # Test that classes exist and have expected methods
        assert hasattr(BulkInvoiceOperations, 'bulk_create_invoices')
        assert hasattr(BulkInvoiceOperations, 'bulk_update_status')
        assert hasattr(BulkClientOperations, 'bulk_import_clients')
        assert hasattr(BulkReporting, 'generate_bulk_report')
        print("✓ All bulk operation methods exist")
        
        return True
    except Exception as e:
        print(f"✗ Bulk operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_advanced_reporting():
    """Test advanced reporting module"""
    print("\nTesting advanced reporting...")
    try:
        from src.business.advanced_reporting import AdvancedReporting
        print("✓ Advanced reporting module imported")
        
        # Test that class has expected methods
        assert hasattr(AdvancedReporting, 'revenue_trend_analysis')
        assert hasattr(AdvancedReporting, 'expense_breakdown_analysis')
        assert hasattr(AdvancedReporting, 'client_performance_metrics')
        assert hasattr(AdvancedReporting, 'project_profitability_analysis')
        assert hasattr(AdvancedReporting, 'predictive_analytics')
        assert hasattr(AdvancedReporting, 'invoice_aging_report')
        print("✓ All reporting methods exist")
        
        return True
    except Exception as e:
        print(f"✗ Advanced reporting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scheduler():
    """Test scheduler module"""
    print("\nTesting scheduler module...")
    try:
        from src.business.scheduler import InvoiceScheduler, NotificationManager
        print("✓ Scheduler module imported")
        
        # Test that classes have expected methods
        assert hasattr(InvoiceScheduler, 'process_recurring_invoices')
        assert hasattr(InvoiceScheduler, 'manual_generate')
        assert hasattr(InvoiceScheduler, 'get_upcoming_invoices')
        assert hasattr(NotificationManager, 'send_invoice_notification')
        assert hasattr(NotificationManager, 'send_batch_reminders')
        print("✓ All scheduler methods exist")
        
        return True
    except Exception as e:
        print(f"✗ Scheduler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test that new modules can be imported together"""
    print("\nTesting module integration...")
    try:
        from src.business import (
            BulkInvoiceOperations,
            AdvancedReporting,
            InvoiceScheduler
        )
        print("✓ All new modules can be imported via business package")
        return True
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("New Features Test Suite")
    print("=" * 60)
    
    results = {
        'Bulk Operations': test_bulk_operations(),
        'Advanced Reporting': test_advanced_reporting(),
        'Scheduler': test_scheduler(),
        'Integration': test_integration()
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 60)
    
    if all(results.values()):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
