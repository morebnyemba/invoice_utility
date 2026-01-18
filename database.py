"""
Database abstraction layer supporting SQLite, PostgreSQL, and MySQL
"""
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration from environment variables"""
    db_type: str = os.getenv("DB_TYPE", "sqlite").lower()  # sqlite, postgresql, mysql
    
    # SQLite
    db_name: str = os.getenv("DB_NAME", "invoices.db")
    
    # PostgreSQL/MySQL
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))  # 5432 for PostgreSQL, 3306 for MySQL
    db_user: str = os.getenv("DB_USER", "")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_database: str = os.getenv("DB_DATABASE", "invoice_db")
    
    # Connection pool settings
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

db_config = DatabaseConfig()

# Try to import database drivers (optional for backward compatibility)
try:
    if db_config.db_type == "postgresql":
        import psycopg2
        from psycopg2 import pool
        from psycopg2.extras import RealDictCursor
        POSTGRESQL_AVAILABLE = True
    else:
        POSTGRESQL_AVAILABLE = False
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    if db_config.db_type == "mysql":
        import mysql.connector
        from mysql.connector import pooling
        MYSQL_AVAILABLE = True
    else:
        MYSQL_AVAILABLE = False
except ImportError:
    MYSQL_AVAILABLE = False

# Global connection pool
_connection_pool = None

def init_connection_pool():
    """Initialize database connection pool for PostgreSQL/MySQL"""
    global _connection_pool
    
    if db_config.db_type == "postgresql" and POSTGRESQL_AVAILABLE:
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,
            db_config.pool_size,
            host=db_config.db_host,
            port=db_config.db_port,
            database=db_config.db_database,
            user=db_config.db_user,
            password=db_config.db_password
        )
    elif db_config.db_type == "mysql" and MYSQL_AVAILABLE:
        _connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="invoice_pool",
            pool_size=db_config.pool_size,
            host=db_config.db_host,
            port=db_config.db_port,
            database=db_config.db_database,
            user=db_config.db_user,
            password=db_config.db_password
        )

@contextmanager
def get_db_connection():
    """
    Context manager for database connections with error handling.
    Supports SQLite, PostgreSQL, and MySQL
    """
    conn = None
    cursor = None
    
    try:
        if db_config.db_type == "sqlite":
            conn = sqlite3.connect(db_config.db_name, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
            
        elif db_config.db_type == "postgresql" and POSTGRESQL_AVAILABLE:
            if _connection_pool is None:
                init_connection_pool()
            conn = _connection_pool.getconn()
            conn.autocommit = False
            yield PostgreSQLConnectionWrapper(conn)
            
        elif db_config.db_type == "mysql" and MYSQL_AVAILABLE:
            if _connection_pool is None:
                init_connection_pool()
            conn = _connection_pool.get_connection()
            yield MySQLConnectionWrapper(conn)
            
        else:
            # Fallback to SQLite if the requested database is not available
            conn = sqlite3.connect(db_config.db_name, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
            
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise
    finally:
        if conn:
            if db_config.db_type == "postgresql" and POSTGRESQL_AVAILABLE and _connection_pool:
                _connection_pool.putconn(conn)
            else:
                conn.close()


class PostgreSQLConnectionWrapper:
    """Wrapper to make PostgreSQL connection compatible with SQLite API"""
    
    def __init__(self, conn):
        self._conn = conn
        self._cursor = None
    
    def execute(self, query: str, params: Tuple = None):
        """Execute a query with parameter substitution"""
        # Convert ? placeholders to %s for PostgreSQL
        query = query.replace("?", "%s")
        self._cursor = self._conn.cursor(cursor_factory=RealDictCursor)
        self._cursor.execute(query, params or ())
        return self
    
    def fetchone(self):
        """Fetch one result"""
        if self._cursor:
            result = self._cursor.fetchone()
            return dict(result) if result else None
        return None
    
    def fetchall(self):
        """Fetch all results"""
        if self._cursor:
            results = self._cursor.fetchall()
            return [dict(row) for row in results]
        return []
    
    def commit(self):
        """Commit transaction"""
        self._conn.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self._conn.rollback()
    
    def close(self):
        """Close connection"""
        if self._cursor:
            self._cursor.close()
        # Don't close the actual connection, let the pool manage it
    
    def backup(self, target_conn):
        """Backup not supported for PostgreSQL"""
        raise NotImplementedError("Backup is only supported for SQLite")


class MySQLConnectionWrapper:
    """Wrapper to make MySQL connection compatible with SQLite API"""
    
    def __init__(self, conn):
        self._conn = conn
        self._cursor = None
    
    def execute(self, query: str, params: Tuple = None):
        """Execute a query with parameter substitution"""
        # Convert ? placeholders to %s for MySQL
        query = query.replace("?", "%s")
        self._cursor = self._conn.cursor(dictionary=True)
        self._cursor.execute(query, params or ())
        return self
    
    def fetchone(self):
        """Fetch one result"""
        if self._cursor:
            return self._cursor.fetchone()
        return None
    
    def fetchall(self):
        """Fetch all results"""
        if self._cursor:
            return self._cursor.fetchall()
        return []
    
    def commit(self):
        """Commit transaction"""
        self._conn.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self._conn.rollback()
    
    def close(self):
        """Close connection"""
        if self._cursor:
            self._cursor.close()
        # Don't close the actual connection, let the pool manage it
    
    def backup(self, target_conn):
        """Backup not supported for MySQL"""
        raise NotImplementedError("Backup is only supported for SQLite")


def get_db_type():
    """Get the current database type"""
    return db_config.db_type


def is_sqlite():
    """Check if using SQLite"""
    return db_config.db_type == "sqlite"
