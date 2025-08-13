from flask import Flask, request, send_file, render_template, after_this_request
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfWriter, PdfReader
import ffmpeg
import zipfile
import os
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cleanup_files(paths):
    @after_this_request
    def cleanup(response):
        for path in paths:
            try:
                os.remove(path)
            except Exception:
                pass
        return response

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():

    action = request.form.get('action')
    # Aceita tanto 'file' quanto 'zipfiles' (compatível com ambos os formulários)
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        files = request.files.getlist('zipfiles')
    filepaths = []
    filenames = []

    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        filepaths.append(filepath)
        filenames.append(filename)

    if not filenames:
        return 'Nenhum arquivo enviado.', 400

    name_without_ext = os.path.splitext(filenames[0])[0]

    # ZIP
    if action == 'zipfile':
        zip_path = os.path.join(UPLOAD_FOLDER, f"{name_without_ext}.zip")
        try:
            log_msgs = []
            total_size = 0
            for fp in filepaths:
                try:
                    size = os.path.getsize(fp)
                    log_msgs.append(f"Arquivo: {fp} | Tamanho: {size} bytes")
                    total_size += size
                except Exception as e:
                    log_msgs.append(f"Erro ao obter tamanho de {fp}: {e}")
            log_msgs.append(f"Tamanho total dos arquivos: {total_size} bytes")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for fp, fn in zip(filepaths, filenames):
                    try:
                        zipf.write(fp, arcname=fn)
                        log_msgs.append(f"Adicionado ao ZIP: {fn}")
                    except Exception as e:
                        log_msgs.append(f"Erro ao adicionar {fn} ao ZIP: {e}")
            cleanup_files(filepaths + [zip_path])
            return send_file(zip_path, as_attachment=True)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            log_msgs.append(f"Exceção ao compactar: {str(e)}\n{tb}")
            # Salva log detalhado para depuração
            with open(os.path.join(UPLOAD_FOLDER, 'zip_error.log'), 'w', encoding='utf-8') as logf:
                logf.write('\n'.join(log_msgs))
            return f'Erro ao compactar: {str(e)}. Veja zip_error.log para detalhes.', 500

    # PDF → Word
    elif action == 'pdf2word' and filenames[0].lower().endswith('.pdf'):
        docx_path = os.path.join(UPLOAD_FOLDER, f"{name_without_ext}.docx")
        try:
            cv = Converter(filepaths[0])
            cv.convert(docx_path, start=0, end=None)
            cv.close()
            cleanup_files([filepaths[0], docx_path])
            return send_file(docx_path, as_attachment=True)
        except Exception as e:
            return f'Erro ao converter PDF: {str(e)}', 500

    # Word → PDF
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
            cleanup_files([filepaths[0], pdf_path])
            return send_file(pdf_path, as_attachment=True)
        except Exception as e:
            return f'Erro ao converter Word: {str(e)}', 500

    # MP4 → MP3
    elif action == 'video2mp3' and filenames[0].lower().endswith('.mp4'):
        mp3_path = os.path.join(UPLOAD_FOLDER, f"{name_without_ext}.mp3")
        try:
            (
                ffmpeg
                .input(filepaths[0])
                .output(mp3_path, format='mp3', acodec='libmp3lame', audio_bitrate='128k')
                .run(overwrite_output=True)
            )
            cleanup_files([filepaths[0], mp3_path])
            return send_file(mp3_path, as_attachment=True)
        except Exception as e:
            return f'Erro ao converter vídeo: {str(e)}', 500

    return 'Arquivo ou ação inválida. Envie PDF, DOCX, MP4 ou selecione ZIP.', 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
