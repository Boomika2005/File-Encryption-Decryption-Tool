import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from cryptography.fernet import Fernet
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
SECRET_KEY = Fernet.generate_key()
fernet = Fernet(SECRET_KEY)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_flask_key'  # for flashing messages

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    if 'file' not in request.files:
        flash('No file uploaded!')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected!')
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with open(filepath, 'rb') as original_file:
        original_data = original_file.read()

    encrypted_data = fernet.encrypt(original_data)
    encrypted_path = filepath + '.encrypted'
    with open(encrypted_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)

    return send_from_directory(directory=UPLOAD_FOLDER, path=os.path.basename(encrypted_path), as_attachment=True)

@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    if 'file' not in request.files:
        flash('No file uploaded!')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected!')
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with open(filepath, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception:
        flash('Invalid file or key for decryption!')
        return redirect(url_for('index'))

    decrypted_path = filepath + '.decrypted'
    with open(decrypted_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

    return send_from_directory(directory=UPLOAD_FOLDER, path=os.path.basename(decrypted_path), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
