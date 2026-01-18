# First-Time Setup Guide

## Welcome! 🎉

This invoice utility is now ready to be configured for YOUR business. Follow these simple steps to get started.

## Step 1: Initial Setup (1 minute)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the application:**
   ```bash
   streamlit run app.py
   ```

3. **Create your admin account:**
   - Open the application in your browser (usually http://localhost:8501)
   - Create a username and password
   - The application works 100% **OFFLINE** - no internet connection needed for core features

## Step 2: Configure Your Business Details (2 minutes)

After logging in, go to **Settings → Company & Invoice** and update:

### Required Information:
- **Company Name**: Your business name
- **Address**: Your business address
- **Phone**: Your contact number
- **Email**: Your business email
- **TIN/Tax ID**: Your tax identification number

### Payment Details:
Replace the default text with your actual payment information:
```html
<b>Payment Details:</b><br/>
Bank Name: Your Bank Name<br/>
Account Number: 1234567890<br/>
Account Name: Your Business Name<br/>
Mobile Money: +1234567890 (if applicable)<br/>
```

**Click "Save Company Settings"** and you're done!

## Step 3: Start Using (immediately)

You can now:
- ✅ Create invoices with your business details
- ✅ Manage clients and projects
- ✅ Track payments and expenses
- ✅ Generate reports
- ✅ Everything works **OFFLINE** (no internet required)

## Optional: Email Configuration

If you want to send invoices via email:
1. Go to **Settings → Email (SMTP)**
2. Configure your email server settings
3. Set `SMTP_PASSWORD` as environment variable
4. This feature requires internet connection when sending emails

**Note:** Email is completely optional. All core features work offline.

## Offline Operation ✈️

This application is designed to work completely offline:

✅ **Works WITHOUT Internet:**
- Creating invoices
- Managing clients and projects
- Recording payments
- Tracking expenses
- Generating reports
- Database operations (SQLite/PostgreSQL/MySQL)
- PDF generation
- All core business features

❌ **Requires Internet (Optional):**
- Sending invoices via email (optional feature)
- Downloading database drivers for PostgreSQL/MySQL (one-time setup)
- Installing Python packages (one-time setup)

Once installed and configured, you can use this application on a computer without any internet connection!

## Database Options

**Default (No Setup Needed):**
- SQLite - Works offline, no configuration required
- Perfect for small to medium businesses
- All your data stored locally in `invoices.db`

**Optional (For Larger Deployments):**
- PostgreSQL or MySQL for multi-user setups
- See `DATABASE_SETUP.md` for details
- Can be hosted locally (no internet needed) or remotely

## Need Help?

- Quick Start: See `QUICKSTART.md`
- Full Documentation: See `README.md`
- Database Setup: See `DATABASE_SETUP.md`
- Run Tests: `python3 test_system.py`

## Tips

1. **Backup your data regularly**: Use Settings → Database & Security → Create Database Backup
2. **Your data is local**: Everything stored on your computer in `invoices.db`
3. **No tracking**: This app doesn't send any data anywhere
4. **Privacy first**: All your business data stays on your device

---

**Ready to start?** Configure your business details in Settings and create your first invoice!
