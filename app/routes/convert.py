
from flask import Blueprint, request, render_template
from app.services.convert_service import handle_conversion

convert_bp = Blueprint('convert', __name__)



@convert_bp.route('/convert', methods=['POST'])
def convert():
	return handle_conversion(request)
