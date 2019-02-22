
import io
import pandas as pd
import xlsxwriter


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
def detect_text(path,output_filename=None):
    """Detects text in the file."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    # path = '/home/niket/Desktop/OCR/test5.jpg'
    
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
   
    final_df = pd.DataFrame({'keys': keys, 'values':values})
    filename_to_save='result_'+output_filename.split('/')[-1]+".xlsx"
    writer = pd.ExcelWriter(filename_to_save, engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    final_df.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    return "saved"
    '''
    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))
    '''



print detect_text('/home/shivam/Desktop/visiondemo/test5.jpg','result_demo')
