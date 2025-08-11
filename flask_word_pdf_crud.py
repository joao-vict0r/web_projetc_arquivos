from flask import Flask, request, send_file, render_template
import os
from werkzeug.utils import secure_filename
from io import BytesIO


# Instale as dependências: pdf2docx, python-docx, pypdf, moviepy
# pip install flask pdf2docx python-docx pypdf moviepy
from moviepy.editor import VideoFileClip

from pdf2docx import Converter
from docx import Document
from pypdf import PdfWriter, PdfReader

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

 # HTML agora está em templates/index.html

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
	file = request.files['file']
	action = request.form['action']
	filename = secure_filename(file.filename)
	filepath = os.path.join(UPLOAD_FOLDER, filename)
	file.save(filepath)

	if action == 'pdf2word' and filename.lower().endswith('.pdf'):
		docx_path = os.path.join(UPLOAD_FOLDER, filename + '.docx')
		cv = Converter(filepath)
		cv.convert(docx_path, start=0, end=None)
		cv.close()
		return send_file(docx_path, as_attachment=True)
	elif action == 'word2pdf' and filename.lower().endswith('.docx'):
		pdf_path = os.path.join(UPLOAD_FOLDER, filename + '.pdf')
		doc = Document(filepath)
		# Simples: converte cada parágrafo em uma página PDF
		pdf_writer = PdfWriter()
		for para in doc.paragraphs:
			# Adiciona texto como página (simples, sem formatação)
			from reportlab.pdfgen import canvas
			from reportlab.lib.pagesizes import letter
			packet = BytesIO()
			can = canvas.Canvas(packet, pagesize=letter)
			can.drawString(100, 750, para.text)
			can.save()
			packet.seek(0)
			pdf_reader = PdfReader(packet)
			pdf_writer.add_page(pdf_reader.pages[0])
		with open(pdf_path, 'wb') as f:
			pdf_writer.write(f)
		return send_file(pdf_path, as_attachment=True)
	elif action == 'video2mp3' and filename.lower().endswith('.mp4'):
		mp3_path = os.path.join(UPLOAD_FOLDER, filename + '.mp3')
		try:
			clip = VideoFileClip(filepath)
			clip.audio.write_audiofile(mp3_path)
			clip.close()
			return send_file(mp3_path, as_attachment=True)
		except Exception as e:
			return f'Erro ao converter vídeo: {str(e)}', 500
	else:
		return 'Arquivo ou ação inválida. Envie PDF, DOCX ou MP4.', 400

if __name__ == '__main__':
	app.run(port=5001, debug=True)
