import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

# Configuration
UPLOAD_FOLDER = '/var/www/html/uploads'
ALLOWED_EXTENSIONS = {'txt', 'php'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '313374@x0r'  # Hardcoded secret for demonstration purposes

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/index.html',methods=['GET'])
def index():
        if request.method == 'POST':
        # Check if the 'file' part is in the request
        if 'file' not in request.files:
            flash('No file part in the request')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        # Check if the file has an allowed extension
        if not allowed_file(file.filename):
            flash('File type not allowed')
            return redirect(request.url)
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Ensure the upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.chmod(app.config['UPLOAD_FOLDER'], 0o777)  # Intentionally insecure
        
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            os.chmod(filepath, 0o777)  # Intentionally insecure
            flash(f'File {filename} successfully uploaded')
            return f'''File uploaded successfully: <a href="/uploads/{filename}">here</a>'''
        except Exception as e:
            flash(f'Error uploading file: {e}')
            return redirect(request.url)
        
        return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        # Check if the 'file' part is in the request
        if 'file' not in request.files:
            flash('No file part in the request')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        # Check if the file has an allowed extension
        if not allowed_file(file.filename):
            flash('File type not allowed')
            return redirect(request.url)
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Ensure the upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.chmod(app.config['UPLOAD_FOLDER'], 0o777)  # Intentionally insecure
        
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            os.chmod(filepath, 0o777)  # Intentionally insecure
            flash(f'File {filename} successfully uploaded')
            return f'''File uploaded successfully: <a href="/uploads/{filename}">here</a>'''
        except Exception as e:
            flash(f'Error uploading file: {e}')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/uploads/<name>')
def download_file(name):
    # Serve files from the upload directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)

if __name__ == '__main__':
    # Running on port 80 with debug mode enabled (intentionally insecure)
    app.run(host='0.0.0.0', port=5000, debug=True)