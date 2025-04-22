import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/var/www/html/uploads'
ALLOWED_EXTENSIONS = {'txt', 'php'}

app = Flask(__name__)
app.config = UPLOAD_FOLDER
app.secret = '313374@x0r'

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
        if not os.path.exists(app.config):
            os.makedirs(app.config, exist_ok=True)
            os.chmod(app.config, 0o777)
        filepath = os.path.join(app.config, filename)
        try:
            file.save(filepath)
            os.chmod(filepath, 0o777)
            flash(f'File {filename} successfully uploaded')
            return f'''File uploaded successfully: <a href="/uploads/{filename}">here</a>'''
        except Exception as e:
            flash(f'Error uploading file: {e}')
            return redirect(request.url)
    return render_template('upload.html')

from flask import send_from_directory
@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config, name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)