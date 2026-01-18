#!/usr/bin/env python3
"""
Test script to verify database connectivity and modules
"""
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    try:
        from src.models import database
        print("✓ database module imported")
    except ImportError as e:
        print(f"✗ Failed to import database: {e}")
        return False
    
    try:
        from src.models import db_schema
        print("✓ db_schema module imported")
    except ImportError as e:
        print(f"✗ Failed to import db_schema: {e}")
        return False
    
    try:
        from src.business import business_logic
        print("✓ business_logic module imported")
    except ImportError as e:
        print(f"✗ Failed to import business_logic: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from src.models.database import get_db_connection, get_db_type
        from src.models.db_schema import check_database_health
        
        db_type = get_db_type()
        print(f"✓ Database type: {db_type}")
        
        # Try to connect
        with get_db_connection() as conn:
            print("✓ Database connection successful")
        
        # Check database health
        health, message = check_database_health()
        if health:
            print(f"✓ Database health check: {message}")
        else:
            print(f"⚠ Database health check: {message}")
        
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_business_logic():
    """Test business logic modules"""
    print("\nTesting business logic modules...")
    try:
        from src.business.business_logic import (
            TaxCalculator, CurrencyConverter, InvoiceTemplate,
            RecurringInvoice, RoleManager
        )
        
        # Test tax calculation
        result = TaxCalculator.calculate_tax(100, 15, "VAT")
        assert result['total'] == 115, "Tax calculation failed"
        print("✓ Tax calculation works")
        
        # Test currency conversion
        converted = CurrencyConverter.convert(100, "USD", "USD")
        assert converted == 100, "Currency conversion failed"
        print("✓ Currency conversion works")
        
        # Test currency formatting
        formatted = CurrencyConverter.format_currency(1000, "USD")
        assert "$" in formatted, "Currency formatting failed"
        print("✓ Currency formatting works")
        
        return True
    except Exception as e:
        print(f"✗ Business logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Invoice Utility - System Test")
    print("=" * 60)
    
    # Print environment info
    print(f"\nPython version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Get DB configuration
    db_type = os.getenv("DB_TYPE", "sqlite")
    print(f"Configured database type: {db_type}")
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Business Logic", test_business_logic()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    # Overall result
    all_passed = all(result for _, result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
