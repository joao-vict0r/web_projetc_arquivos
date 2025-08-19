from flask import after_this_request
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

def cleanup_files(paths):
    @after_this_request
    def cleanup(response):
        for path in paths:
            try:
                if os.path.abspath(path).startswith(os.path.abspath(UPLOAD_FOLDER)):
                    os.remove(path)
            except Exception:
                pass
        return response
    return cleanup
