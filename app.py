from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
import os
from flask import Flask, flash, request, redirect, url_for,request
from werkzeug.utils import secure_filename
from converting_excel import make_key_value

from flask import send_from_directory
import pandas as pd
import pdftables_api


UPLOAD_FOLDER = os.getcwd()+"/uploads"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','xlsx'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app config

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # filen = open('uploads/'+filename, "r")
    # for line in filen:
    #     print line,
    extension=filename.split('.')[-1].lower()
    if extension=='xlsx':
        make_key_value('uploads/'+filename)
    elif extension=='pdf':
        c = pdftables_api.Client('tdjdrag6bh6p')
        c.xlsx('uploads/'+filename, 'output_'+filename)
    else:
        print "Image"
        'Todo'
    return "Uploaded"



if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)