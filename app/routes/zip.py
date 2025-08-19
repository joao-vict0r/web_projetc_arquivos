
from flask import Blueprint, send_from_directory, abort
import os

zip_bp = Blueprint('zip', __name__)

# Rota para download de arquivos extraídos
@zip_bp.route('/download_extracted/<extract_dir>/<path:filename>')
def download_extracted(extract_dir, filename):
	base_extract_path = os.path.join(os.path.dirname(__file__), '../../extracted')
	abs_extract_dir = os.path.abspath(os.path.join(base_extract_path, extract_dir))
	abs_file_path = os.path.abspath(os.path.join(abs_extract_dir, filename))
	# Segurança: só permite download dentro da pasta de extração
	if not abs_file_path.startswith(abs_extract_dir):
		abort(403)
	if not os.path.exists(abs_file_path):
		abort(404)
	return send_from_directory(abs_extract_dir, filename, as_attachment=True)
