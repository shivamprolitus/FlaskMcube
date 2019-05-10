from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
import os
from flask import Flask, flash, request, redirect, url_for,request
from werkzeug.utils import secure_filename
from converting_excel import make_key_value

from flask import send_from_directory,send_file
import pandas as pd
import pdftables_api

import io
import pandas as pd
import xlsxwriter
from wand.image import Image 
from PyPDF2 import PdfFileReader

def isint(text):
    temp=text.split(',')
    for i in temp:
        try:
            float(i)
        except:
            new_temp=i.split('.')
            if len(new_temp):
                for j in new_temp:
                    try:
                        float(j)
                    except:
                        return False
                return True
            return False
    return True

UPLOAD_FOLDER = os.getcwd()+"/uploads"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','xlsx'])

app = Flask(__name__,static_url_path='')
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
    return render_template('upload.html')
    
#  @app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
#     def download(filename):
#     uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
#     return send_from_directory(directory=uploads, filename=filename)

from io import BytesIO
@app.route('/showfile')
def show_file():
    uploads=os.path.join(app.root_path,app.config['UPLOAD_FOLDER'])
    buffer = BytesIO()
    # buffer.write(b'jJust some letters.')
    # Or you can encode it to bytes.
    # buffer.write('Just some letters.'.encode('utf-8'))
    # buffer.seek(0)
    # return send_file(buffer, as_attachment=True,
    #                  attachment_filename='Test_2.pdf.xlsx',
    #                  mimetype='text/xlsx')
    return send_file(uploads+'/'+'Test_1.xlsx',
                     mimetype='text/xlsx',
                     attachment_filename='Test_1.xlsx',
                     as_attachment=True)
    # return send_from_directory(directory=uploads,filename='Test_2.pdf.xlsx')


# def change_pdf_to_image(path):
#     img = Image(filename=path)
#     img.save(filename="temp.jpg")
#     img = Image(filename="temp.jpg")
#     img.resize(1000,1000)
#     img.save(filename=path+".jpg")
    
def change_pdf_to_image(path):
    img = Image(filename=path)
    with Image(filename=path) as image:
        with image.clone() as rotated:
            rotated.rotate(90)
            rotated.save(filename='temp.jpg')

    # img.save(filename="temp.jpg")
    img = Image(filename="temp.jpg")
    img.resize(1000,1000)
    img.save(filename=path+".jpg")

def check_pdf(path):
    '''
        Return true if pdf is pdf or image'
    '''
    try:
        with open(path, 'rb') as f:
            pdf = PdfFileReader(f)
            # get the first page
            page = pdf.getPage(1)
            # print(page)
            # print('Page type: {}'.format(str(type(page))))
            text = page.extractText()
            # print(text)
        return True
    except:
        return False
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # filen = open('uploads/'+filename, "r")
    # for line in filen:
    #     print line,
    # print app.root_path
   
    extension=filename.split('.')[-1].lower()
    # if extension=='pdf':
    #     print filename
    #     uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    #     return send_from_directory(directory=uploads, filename=filename)
    if extension=='xlsx':
        filepath='result_'+filename
        make_key_value('uploads/'+filename,filename)
        return send_from_directory(app.root_path+"/",filepath)

    elif extension=='pdf':
        c = pdftables_api.Client('3zn6uoljmgcp')
        filepath='uploads/'+filename
        if check_pdf(filepath):

            c.xlsx('uploads/'+filename,'uploads/'+filename)
            filename2=filename+'.xlsx'
            uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            return send_file(uploads+'/'+filename2,
                        mimetype='text/xlsx',
                        attachment_filename=filename2,
                        as_attachment=True)
        # return redirect(url_for('show_file',namefile=filename2))
        # return send_from_directory(directory=uploads, namefile=filename2)
        else:
            from google.cloud import vision
            client = vision.ImageAnnotatorClient()
            path='uploads/'+filename
            change_pdf_to_image(path)
            path=path+".jpg"
            with io.open(path, 'rb') as image_file:
                content = image_file.read()

            image = vision.types.Image(content=content)

            response = client.document_text_detection(image=image)
            texts = response.text_annotations
            data_array=[]
            for text in texts:
                data_array.append(text.description)
            result=data_array[0].split('\n')[1:-1]
            dict={}
            keys=[]
            values=[]
            for i in result:
                if isint(i):
                    values.append(i)
                else:
                    keys.append(i)
            
            for k,v in zip(keys,values):
                dict[k]=v
        
            final_df = pd.DataFrame({'Key': keys, 'Value':values})
            filename_to_save='result_'+filename.split('/')[0]+'.xlsx'
            writer = pd.ExcelWriter(filename_to_save, engine='xlsxwriter')
            # Convert the dataframe to an XlsxWriter Excel object.
            final_df.to_excel(writer, sheet_name='Sheet1')
            # Close the Pandas Excel writer and output the Excel file.
            writer.save()
                
            # return send_from_directory(app.root_path+"/",filename_to_save)
            return send_file(filename_to_save,
                        mimetype='text/xlsx',
                        attachment_filename=filename_to_save,
                        as_attachment=True)
            # return send_from_directory(directory=app.root_path, filename=filename_to_save)



if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)