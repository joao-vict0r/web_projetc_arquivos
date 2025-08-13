from flask import Flask, request, send_file, render_template
import os
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from docx import Document
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    action = request.form.get('action')
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    name_without_ext = os.path.splitext(filename)[0]

    if action == 'pdf2word' and filename.lower().endswith('.pdf'):
        docx_path = os.path.join(UPLOAD_FOLDER, f"{name_without_ext}.docx")
        try:
            cv = Converter(filepath)
            cv.convert(docx_path, start=0, end=None)
            cv.close()
        except Exception as e:
            return f'Erro ao converter PDF: {e}', 500
        return send_file(docx_path, as_attachment=True)

    elif action == 'word2pdf' and filename.lower().endswith('.docx'):
        pdf_path = os.path.join(UPLOAD_FOLDER, f"{name_without_ext}.pdf")
        try:
            doc = Document(filepath)
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            y = 750
            for para in doc.paragraphs:
                can.drawString(100, y, para.text)
                y -= 20
            can.save()
            packet.seek(0)
            with open(pdf_path, 'wb') as f:
                f.write(packet.read())
        except Exception as e:
            return f'Erro ao converter Word: {e}', 500
        return send_file(pdf_path, as_attachment=True)

    else:
        return 'Arquivo ou ação inválida. Envie PDF ou DOCX.', 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
import zipfile
import ffmpeg
from flask import Flask, request, send_file, render_template, after_this_request
import os
from werkzeug.utils import secure_filename
from io import BytesIO
from pdf2docx import Converter
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from pypdf import PdfWriter, PdfReader
#from docx2pdf import convert

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    action = request.form['action']
    name_without_ext = None
    filepaths = []
    filenames = []
    # Suporte a múltiplos arquivos para ZIP
    if action == 'zipfile':
        files = request.files.getlist('file')
        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            filepaths.append(filepath)
            filenames.append(filename)
        name_without_ext = 'arquivos'
    else:
        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        filepaths.append(filepath)
        filenames.append(filename)
        name_without_ext = os.path.splitext(filename)[0]

    if action == 'zipfile':
        zip_path = os.path.join(UPLOAD_FOLDER, f"{name_without_ext}.zip")
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for fp, fn in zip(filepaths, filenames):
                    zipf.write(fp, arcname=fn)
            @after_this_request
            def cleanup(response):
                try:
                    for fp in filepaths:
                        os.remove(fp)
                    os.remove(zip_path)
                except Exception:
                    pass
                return response
            return send_file(zip_path, as_attachment=True)
        except Exception as e:
            return f'Erro ao compactar arquivo: {str(e)}', 500

    elif action == 'pdf2word' and filenames[0].lower().endswith('.pdf'):
        docx_path = os.path.join(UPLOAD_FOLDER, f"{name_without_ext}.docx")
        cv = Converter(filepaths[0])
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        @after_this_request
        def cleanup(response):
            try:
                os.remove(filepaths[0])
                os.remove(docx_path)
            except Exception:
                pass
            return response
        return send_file(docx_path, as_attachment=True)

    elif action == 'word2pdf' and filenames[0].lower().endswith('.docx'):
        pdf_path = os.path.join(UPLOAD_FOLDER, f"{name_without_ext}.pdf")
        try:
            doc = Document(filepaths[0])
            pdf_writer = PdfWriter()
            for para in doc.paragraphs:
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.drawString(100, 750, para.text)
                can.save()
                packet.seek(0)
                pdf_reader = PdfReader(packet)
                pdf_writer.add_page(pdf_reader.pages[0])
            with open(pdf_path, 'wb') as f:
                pdf_writer.write(f)
        except Exception as e:
            return f'Erro ao converter Word: {e}', 500
        @after_this_request
        def cleanup(response):
            os.remove(filepaths[0])
            os.remove(pdf_path)
            return response
        return send_file(pdf_path, as_attachment=True)

    elif action == 'video2mp3' and filenames[0].lower().endswith('.mp4'):
        mp3_path = os.path.join(UPLOAD_FOLDER, f"{name_without_ext}.mp3")
        try:
            (
                ffmpeg
                .input(filepaths[0])
                .output(mp3_path, format='mp3', acodec='libmp3lame', audio_bitrate='128k')
                .run(overwrite_output=True)
            )
            @after_this_request
            def cleanup(response):
                try:
                    os.remove(filepaths[0])
                    os.remove(mp3_path)
                except Exception:
                    pass
                return response
            return send_file(mp3_path, as_attachment=True)
        except Exception as e:
            return f'Erro ao converter vídeo: {str(e)}', 500

    else:
        return 'Arquivo ou ação inválida. Envie PDF, DOCX, MP4 ou selecione ZIP.', 400

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True, host='0.0.0.0', port=5000)