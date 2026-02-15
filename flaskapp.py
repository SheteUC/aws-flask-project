from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/var/www/html/flaskapp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    conn = sqlite3.connect('/var/www/html/flaskapp/users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, firstname TEXT, lastname TEXT, email TEXT, address TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        address = request.form['address']
        
        conn = sqlite3.connect('/var/www/html/flaskapp/users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)",
                  (username, password, firstname, lastname, email, address))
        conn.commit()
        conn.close()
        return redirect(url_for('profile', username=username))
    except Exception as e:
        return f"Error: {e}"

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect('/var/www/html/flaskapp/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return redirect(url_for('profile', username=username))
    else:
        return "Invalid credentials. <a href='/login_page'>Try again</a>"

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect('/var/www/html/flaskapp/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/upload/<username>', methods=['POST'])
def upload_file(username):
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Count words
        with open(filepath, 'r') as f:
            content = f.read()
            word_count = len(content.split())
            
        return render_template('profile.html', 
                               user=None,
                               username=username,
                               word_count=word_count, 
                               filename=file.filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run()
