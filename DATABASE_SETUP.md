# Database Configuration Guide

## Overview

The Invoice Utility now supports multiple database backends for production-ready deployments:
- **SQLite** (default) - File-based, perfect for small businesses
- **PostgreSQL** - Enterprise-grade relational database
- **MySQL** - Popular open-source database

## Quick Start (SQLite - Default)

No configuration needed! The application uses SQLite by default with a local `invoices.db` file.

## PostgreSQL Setup

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
```

### 2. Create Database

```bash
sudo -u postgres psql
CREATE DATABASE invoice_db;
CREATE USER invoice_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE invoice_db TO invoice_user;
\q
```

### 3. Configure Environment Variables

Create a `.env` file or set environment variables:

```bash
export DB_TYPE=postgresql
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=invoice_user
export DB_PASSWORD=your_secure_password
export DB_DATABASE=invoice_db
export DB_POOL_SIZE=5
export DB_MAX_OVERFLOW=10
```

### 4. Install Python Dependencies

```bash
pip install psycopg2-binary>=2.9.0
```

## MySQL Setup

### 1. Install MySQL

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install mysql-server
```

**macOS:**
```bash
brew install mysql
```

### 2. Create Database

```bash
mysql -u root -p
CREATE DATABASE invoice_db;
CREATE USER 'invoice_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON invoice_db.* TO 'invoice_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Configure Environment Variables

```bash
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=invoice_user
export DB_PASSWORD=your_secure_password
export DB_DATABASE=invoice_db
export DB_POOL_SIZE=5
export DB_MAX_OVERFLOW=10
```

### 4. Install Python Dependencies

```bash
pip install mysql-connector-python>=8.0.0
```

## Connection Pooling

The application automatically uses connection pooling for PostgreSQL and MySQL:

- `DB_POOL_SIZE`: Initial number of connections (default: 5)
- `DB_MAX_OVERFLOW`: Maximum additional connections (default: 10)

## Migration from SQLite

To migrate from SQLite to PostgreSQL/MySQL:

1. **Backup your SQLite database** using the application's backup feature
2. Set up your new database (PostgreSQL or MySQL)
3. Configure environment variables
4. Restart the application - it will initialize the new database schema
5. Export data from SQLite and import into the new database (manual process)

## Production Deployment Checklist

- [ ] Use PostgreSQL or MySQL for production
- [ ] Enable connection pooling
- [ ] Set secure database passwords
- [ ] Configure firewall rules for database access
- [ ] Enable database backups (automated)
- [ ] Monitor database performance
- [ ] Use SSL/TLS for database connections
- [ ] Implement regular security audits

## Troubleshooting

### Connection Errors

**Issue:** Cannot connect to database
**Solution:** 
- Check database is running: `systemctl status postgresql` or `systemctl status mysql`
- Verify credentials and permissions
- Check firewall rules

### Performance Issues

**Issue:** Slow queries
**Solution:**
- Increase connection pool size
- Add database indexes
- Optimize queries
- Monitor slow query logs

### Migration Issues

**Issue:** Schema differences
**Solution:**
- Application automatically handles schema migrations
- Check logs for any migration errors
- Ensure database user has CREATE TABLE permissions

## Security Best Practices

1. **Never commit database credentials** to version control
2. Use **environment variables** for configuration
3. Use **strong passwords** for database users
4. Enable **SSL/TLS** for remote connections
5. Implement **regular backups**
6. Restrict database access to **application server only**
7. Keep database software **up to date**

## Performance Tuning

### PostgreSQL

```sql
-- Increase shared buffers (25% of RAM)
ALTER SYSTEM SET shared_buffers = '1GB';

-- Enable query planning
ALTER SYSTEM SET effective_cache_size = '4GB';
```

### MySQL

```sql
-- Increase buffer pool (70% of RAM)
SET GLOBAL innodb_buffer_pool_size = 1073741824;

-- Enable query cache
SET GLOBAL query_cache_size = 268435456;
```

## Support

For issues or questions:
- Check application logs
- Review database logs
- Consult database documentation
- Check application settings page for database health status
