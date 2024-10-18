
from flask import Flask, flash, request, redirect, make_response
import aspose.slides as slides
import io

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'pdf'}

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

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            with slides.Presentation() as pres:
                pres.slides.remove_at(0)

                pres.slides.add_from_pdf(io.BytesIO(file.read()))

                ppt_bytes_io = io.BytesIO()
                pres.save(ppt_bytes_io, slides.export.SaveFormat.PPTX)
                ppt_bytes_io.seek(0)
           
            response = make_response(ppt_bytes_io.getvalue())
            response.headers['Content-Disposition'] = 'attachment; filename=presentation.pptx'
            response.mimetype = 'application/vnd.ms-powerpoint'
            return response
            

    return '''
    <!doctype html>
    <title>Upload PDF</title>
    <h1>Covnert PDF to PPTX</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":
    if __name__ == "__main__":
        app.run(debug=True, port=4000)
