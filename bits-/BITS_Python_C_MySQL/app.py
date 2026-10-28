from __future__ import annotations
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'app', 'templates'), static_folder=os.path.join(BASE_DIR, 'app', 'static'))
app.secret_key = os.environ.get('BITS_SECRET_KEY', 'change-this-demo-secret-before-deployment')

DB_CONFIG = {
    'host': os.environ.get('BITS_DB_HOST', 'localhost'),
    'port': int(os.environ.get('BITS_DB_PORT', '3306')),
    'user': os.environ.get('BITS_DB_USER', 'root'),
    'password': os.environ.get('BITS_DB_PASSWORD', ''),
    'database': os.environ.get('BITS_DB_NAME', 'bits_inventory'),
    'connection_timeout': 5,
}

def db():
    if 'db_conn' not in g:
        g.db_conn = mysql.connector.connect(**DB_CONFIG)
    return g.db_conn

@app.teardown_appcontext
def close_db(_exc=None):
    conn = g.pop('db_conn', None)
    if conn is not None and conn.is_connected():
        conn.close()

def init_schema():
    """Create namespaced tables so the Python app can coexist with the Java edition."""
    conn = mysql.connector.connect(**{k:v for k,v in DB_CONFIG.items() if k != 'database'})
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database'].replace('`','')}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.close(); conn.close()
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    statements = [
      """CREATE TABLE IF NOT EXISTS web_users (
        id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL,
        email VARCHAR(190) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB""",
      """CREATE TABLE IF NOT EXISTS web_categories (
        id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, name VARCHAR(100) NOT NULL,
        UNIQUE KEY uq_web_category_user_name(user_id,name),
        CONSTRAINT fk_web_category_user FOREIGN KEY(user_id) REFERENCES web_users(id) ON DELETE CASCADE) ENGINE=InnoDB""",
      """CREATE TABLE IF NOT EXISTS web_components (
        id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, category_id INT NULL,
        name VARCHAR(150) NOT NULL, component_value VARCHAR(100) DEFAULT '', quantity INT NOT NULL DEFAULT 0,
        location VARCHAR(150) DEFAULT '', notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_web_components_user(user_id),
        CONSTRAINT fk_web_component_user FOREIGN KEY(user_id) REFERENCES web_users(id) ON DELETE CASCADE,
        CONSTRAINT fk_web_component_category FOREIGN KEY(category_id) REFERENCES web_categories(id) ON DELETE SET NULL,
        CONSTRAINT chk_web_component_quantity CHECK(quantity >= 0)) ENGINE=InnoDB"""
    ]
    for statement in statements: cur.execute(statement)
    conn.commit(); cur.close(); conn.close()

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please sign in to continue.', 'warning')
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapped

def current_user():
    cur = db().cursor(dictionary=True)
    cur.execute('SELECT id,name,email FROM web_users WHERE id=%s', (session['user_id'],))
    user = cur.fetchone(); cur.close()
    return user

@app.context_processor
def inject_user():
    return {'signed_in_user': current_user() if session.get('user_id') else None}

@app.route('/')
def index():
    return redirect(url_for('dashboard') if session.get('user_id') else url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        confirm = request.form.get('confirm_password','')
        if not name or not email or len(password) < 8:
            flash('Enter your name and email, and use a password of at least 8 characters.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        else:
            cur = db().cursor()
            try:
                cur.execute('INSERT INTO web_users(name,email,password_hash) VALUES(%s,%s,%s)', (name,email,generate_password_hash(password)))
                db().commit(); uid = cur.lastrowid
                cur.executemany('INSERT INTO web_categories(user_id,name) VALUES(%s,%s)', [(uid,n) for n in ['Resistors','Capacitors','Inductors','Diodes','Transistors','ICs','Sensors','Development Boards','Connectors','Other']])
                db().commit(); session.clear(); session['user_id'] = uid
                flash('Account created. Welcome to BITS!', 'success')
                return redirect(url_for('dashboard'))
            except mysql.connector.IntegrityError:
                db().rollback(); flash('That email is already registered.', 'danger')
            except Error as exc:
                db().rollback(); flash(f'Database error: {exc}', 'danger')
            finally: cur.close()
    return render_template('auth.html', mode='register')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower(); password = request.form.get('password','')
        cur = db().cursor(dictionary=True)
        cur.execute('SELECT id,name,password_hash FROM web_users WHERE email=%s', (email,)); user = cur.fetchone(); cur.close()
        if user and check_password_hash(user['password_hash'], password):
            session.clear(); session['user_id'] = user['id']; return redirect(url_for('dashboard'))
        flash('Incorrect email or password.', 'danger')
    return render_template('auth.html', mode='login')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear(); flash('You have been signed out.', 'info'); return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']; q = request.args.get('q','').strip(); category_filter = request.args.get('category','').strip()
    cur = db().cursor(dictionary=True)
    cur.execute('SELECT id,name FROM web_categories WHERE user_id=%s ORDER BY name', (user_id,)); categories = cur.fetchall()
    sql = '''SELECT c.id,c.name,c.component_value,c.quantity,c.location,c.notes,c.category_id,COALESCE(cat.name,'Uncategorised') AS category
             FROM web_components c LEFT JOIN web_categories cat ON cat.id=c.category_id
             WHERE c.user_id=%s'''
    params = [user_id]
    if q:
        sql += ' AND (c.name LIKE %s OR c.component_value LIKE %s OR c.location LIKE %s OR COALESCE(cat.name,\'\') LIKE %s)'
        params += [f'%{q}%']*4
    if category_filter.isdigit(): sql += ' AND c.category_id=%s'; params.append(int(category_filter))
    sql += ' ORDER BY c.name'
    cur.execute(sql, tuple(params)); components = cur.fetchall()
    cur.execute('SELECT COUNT(*) AS n, COALESCE(SUM(quantity),0) AS units FROM web_components WHERE user_id=%s', (user_id,)); stats=cur.fetchone()
    cur.execute('SELECT COUNT(*) AS n FROM web_categories WHERE user_id=%s', (user_id,)); stats['categories']=cur.fetchone()['n']
    cur.close()
    return render_template('dashboard.html', components=components, categories=categories, q=q, category_filter=category_filter, stats=stats)

@app.route('/categories', methods=['POST'])
@login_required
def add_category():
    name=request.form.get('name','').strip()
    if not name or len(name)>100: flash('Category name must be between 1 and 100 characters.', 'danger')
    else:
        cur=db().cursor()
        try: cur.execute('INSERT INTO web_categories(user_id,name) VALUES(%s,%s)',(session['user_id'],name)); db().commit(); flash('Category added to the dropdown.', 'success')
        except mysql.connector.IntegrityError: db().rollback(); flash('That category already exists.', 'warning')
        finally: cur.close()
    return redirect(url_for('dashboard'))

@app.route('/components/save', methods=['POST'])
@login_required
def save_component():
    user_id=session['user_id']; cid=request.form.get('id','').strip(); name=request.form.get('name','').strip()
    value=request.form.get('component_value','').strip(); location=request.form.get('location','').strip(); notes=request.form.get('notes','').strip()
    try: quantity=int(request.form.get('quantity','0'))
    except ValueError: quantity=-1
    cat=request.form.get('category_id','').strip()
    category_id=int(cat) if cat.isdigit() and int(cat)>0 else None
    if not name or quantity < 0:
        flash('Component name is required and quantity must be zero or greater.', 'danger'); return redirect(url_for('dashboard'))
    cur=db().cursor()
    if category_id:
        cur.execute('SELECT id FROM web_categories WHERE id=%s AND user_id=%s',(category_id,user_id))
        if not cur.fetchone(): category_id=None
    try:
        if cid.isdigit():
            cur.execute('UPDATE web_components SET category_id=%s,name=%s,component_value=%s,quantity=%s,location=%s,notes=%s WHERE id=%s AND user_id=%s',(category_id,name,value,quantity,location,notes,int(cid),user_id))
            flash('Component updated.', 'success')
        else:
            cur.execute('INSERT INTO web_components(user_id,category_id,name,component_value,quantity,location,notes) VALUES(%s,%s,%s,%s,%s,%s,%s)',(user_id,category_id,name,value,quantity,location,notes)); flash('Component added.', 'success')
        db().commit()
    except Error as exc: db().rollback(); flash(f'Could not save component: {exc}', 'danger')
    finally: cur.close()
    return redirect(url_for('dashboard'))

@app.route('/components/<int:component_id>/stock', methods=['POST'])
@login_required
def stock(component_id):
    delta=request.form.get('delta','0')
    if delta not in ('-1','1'): flash('Invalid stock change.', 'danger'); return redirect(url_for('dashboard'))
    cur=db().cursor(); cur.execute('UPDATE web_components SET quantity=quantity+%s WHERE id=%s AND user_id=%s AND quantity+%s>=0',(int(delta),component_id,session['user_id'],int(delta))); db().commit()
    if cur.rowcount == 0: flash('Stock was unchanged. Quantity cannot go below zero.', 'warning')
    else: flash('Stock updated.', 'success')
    cur.close(); return redirect(url_for('dashboard'))

@app.route('/components/<int:component_id>/delete', methods=['POST'])
@login_required
def delete_component(component_id):
    cur=db().cursor(); cur.execute('DELETE FROM web_components WHERE id=%s AND user_id=%s',(component_id,session['user_id'])); db().commit(); cur.close(); flash('Component deleted.', 'info'); return redirect(url_for('dashboard'))

@app.route('/health')
def health():
    try:
        cur=db().cursor(); cur.execute('SELECT 1'); cur.fetchone(); cur.close(); return {'app':'BITS','database':'connected'},200
    except Error as exc: return {'app':'BITS','database':'error','detail':str(exc)},503

if __name__ == '__main__':
    try:
        init_schema()
        print('BITS database tables are ready.')
    except Error as exc:
        print('\nMySQL setup failed:', exc)
        print('Check BITS_DB_HOST, BITS_DB_PORT, BITS_DB_USER, BITS_DB_PASSWORD and BITS_DB_NAME.')
        raise SystemExit(1)
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT','5000')), debug=False)
