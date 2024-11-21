from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import os
from werkzeug.utils import secure_filename
from datetime import datetime


app = Flask(__name__)
app.secret_key = "chave_secreta"
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Admin credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "1234"
}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Routes
@app.route('/')
def home():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        upload_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        files.append({"name": filename, "date": upload_time})
    return render_template('index.html', files=files, admin=session.get('is_admin'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('home'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('home'))

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully!')
        return redirect(url_for('home'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not session.get('is_admin'):
        flash('You are not authorized to delete files.')
        return redirect(url_for('home'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully!')
    else:
        flash('File not found.')
    return redirect(url_for('home'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], 
        filename, 
        as_attachment=True  # Garante o download
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
            session['is_admin'] = True
            flash('Logged in as admin.')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    flash('Logged out successfully.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=True)

