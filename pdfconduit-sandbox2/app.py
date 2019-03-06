import os
from flask import Flask, request, flash, redirect, send_from_directory
from werkzeug.utils import secure_filename
from pdfconduit import Watermark


def apply_watermark(file_path, params):
    # Execute Watermark class
    wm = Watermark(file_path, progress_bar_enabled=False, use_receipt=False)

    wm.draw(text1=params['address'],
            text2=str(params['town'] + ', ' + params['state']))
    return wm.add()


ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * (1024 * 1024)
UPLOAD_FOLDER = '/app/uploads'

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        params = {
            'address': '43 Indian Lane',
            'town': 'Franklin',
            'state': 'MA',
        }

        # If user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # File has been added and validated
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Make uploads directory if it does not exist
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.mkdir(app.config['UPLOAD_FOLDER'])
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Create new watermarked file and return file path
            watermarked = apply_watermark(file_path, params)
            return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(watermarked))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    # docker build -t basic .
    # docker run -i -t -p 5000:5000 basic:latest
    app.run(host='0.0.0.0', port=5000, debug=True)
