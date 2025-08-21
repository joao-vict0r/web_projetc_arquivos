
from flask import Blueprint, render_template, request, send_from_directory, current_app
import os

zip_bp = Blueprint('zip', __name__)

@zip_bp.route('/unzip', methods=['GET', 'POST'])
def unzip():
    if request.method == 'POST':
        # Lógica de descompactação aqui
        return "Arquivo descompactado!"
    return render_template('unzip_list.html')


# Nova rota para download dos arquivos extraídos
@zip_bp.route('/download/<filename>')
def download_extracted(filename):
    directory = os.path.join(current_app.root_path, 'uploads')
    return send_from_directory(directory, filename, as_attachment=True)