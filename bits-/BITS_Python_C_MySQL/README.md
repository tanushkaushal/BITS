# BITS — Bench Inventory & Tracking System (Python + C + MySQL)

A presentation-ready local web app with a workshop-photo background that remains visible on **login, registration, and the dashboard after sign-in**. The dashboard includes category filters and a category dropdown in the Add/Edit Component form. Add categories with **Manage categories**; new categories immediately become dropdown options.

## Stack
- Python 3.10+ and Flask for web routes/session/authentication.
- HTML templates, CSS, and JavaScript for the responsive dark glass-style interface.
- MySQL 8+ for accounts, categories, and component inventory.
- C module (`c/stock_rules.c`) for stock validation rules, with a small CLI demonstration. The main app runs in Python; C is included as a separate reusable/demo module.

## Features
- Account registration/sign-in; passwords stored with Werkzeug's salted password hashing.
- User-specific inventory and categories.
- Pre-populated starter categories for each new account: Resistors, Capacitors, Inductors, Diodes, Transistors, ICs, Sensors, Development Boards, Connectors, Other.
- Category dropdown for add/edit; add custom categories.
- Search and category filter; add/edit/delete parts; stock +/- with no negative quantities.
- Responsive layout; workshop background image remains set on every page.
- MySQL health check at `http://127.0.0.1:5000/health`.
- Namespaced `web_users`, `web_categories`, and `web_components` tables so this edition can coexist with the Java edition's `users`, `categories`, and `components` tables in the same `bits_inventory` database.

## Windows quick start
1. Ensure MySQL service is running and you know your local MySQL username/password.
2. Install Python 3.10 or newer from <https://www.python.org/downloads/windows/>. During installation, select **Add Python to PATH**.
3. Extract this ZIP to a normal folder.
4. Open PowerShell in the extracted folder. Run:
   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\run_windows.ps1
   ```
   The script creates a virtual environment, installs dependencies, asks for the MySQL credentials, creates the database/tables if permitted, and starts the app.
5. Open <http://127.0.0.1:5000> in your browser. Register a new Python-edition account.

Alternative manual setup (PowerShell):
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:BITS_DB_HOST='localhost'
$env:BITS_DB_PORT='3306'
$env:BITS_DB_NAME='bits_inventory'
$env:BITS_DB_USER='root'
$env:BITS_DB_PASSWORD='YOUR_LOCAL_MYSQL_PASSWORD'
$env:BITS_SECRET_KEY='use-a-long-random-local-secret'
python app.py
```

If the MySQL account cannot create databases, run `database/schema.sql` in MySQL Workbench using an account with permission to create tables, then run the app with an account that can read/write the `web_*` tables. The app intentionally does not require altering the existing Java-edition tables.

## C module (optional demonstration)
Install a C compiler such as GCC/MinGW. From the project folder:
```powershell
gcc c/stock_demo.c c/stock_rules.c -o stock_demo.exe
.\stock_demo.exe 5 -1
.\stock_demo.exe 0 -1
```
The first command reports quantity 4; the second rejects the change because stock cannot become negative. The web application itself is served by Python; the C utility is a separate module/demo, not a required runtime dependency.

## Database configuration
Environment variables supported: `BITS_DB_HOST`, `BITS_DB_PORT`, `BITS_DB_NAME`, `BITS_DB_USER`, `BITS_DB_PASSWORD`, `BITS_SECRET_KEY`. Do not commit passwords. Use a dedicated least-privilege MySQL user rather than root for deployment. This package is designed for a local/student presentation and has not undergone an independent security audit; do not expose the development server publicly.

## Troubleshooting
- **Access denied:** confirm credentials by connecting with the same MySQL account in Workbench; check `BITS_DB_USER` and `BITS_DB_PASSWORD` in the launch terminal.
- **Can't connect:** start the `MySQL80` Windows service and confirm host/port.
- **No module named flask/mysql.connector:** activate `.venv` and run `pip install -r requirements.txt`.
- **Port 5000 busy:** set `$env:PORT='5001'` before launch and browse to `http://127.0.0.1:5001`.
- **Background not showing:** keep `app/static/workshop-background.png` in place; the page CSS references `/static/workshop-background.png` across all authenticated and unauthenticated pages.
