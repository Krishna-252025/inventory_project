from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'inventory_secret_key'  # change for production

DB_PATH = Path(__file__).parent / 'inventory.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    quantity INTEGER NOT NULL DEFAULT 0
                );""")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=('GET', 'POST'))
def add_item():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        quantity = request.form.get('quantity', '0').strip()
        
        if not name:
            flash('Item name is required.')
            return redirect(url_for('add_item'))
        
        try:
            qty = int(quantity)
        except:
            flash('Quantity must be a number.')
            return redirect(url_for('add_item'))
        
        conn = get_db_connection()
        conn.execute('INSERT INTO items (name, description, quantity) VALUES (?, ?, ?)',
                     (name, description, qty))
        conn.commit()
        conn.close()
        
        flash('Item added successfully.')
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/update/<int:item_id>', methods=('GET', 'POST'))
def update_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    
    if item is None:
        conn.close()
        flash('Item not found.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        quantity = request.form.get('quantity', '0').strip()

        if not name:
            flash('Item name is required.')
            return redirect(url_for('update_item', item_id=item_id))

        try:
            qty = int(quantity)
        except:
            flash('Quantity must be a number.')
            return redirect(url_for('update_item', item_id=item_id))

        conn.execute('UPDATE items SET name = ?, description = ?, quantity = ? WHERE id = ?',
                     (name, description, qty, item_id))
        conn.commit()
        conn.close()

        flash('Item updated successfully.')
        return redirect(url_for('index'))

    conn.close()
    return render_template('update.html', item=item)

@app.route('/delete/<int:item_id>', methods=('POST',))
def delete_item(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    flash('Item deleted.')
    return redirect(url_for('index'))


# ------------------------------
# IMPORTANT FOR RENDER DEPLOYMENT
# ------------------------------

# Always initialize DB — Render needs this!
init_db()

if __name__ == "__main__":
    app.run()
