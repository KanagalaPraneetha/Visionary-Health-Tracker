from flask import Blueprint, request, jsonify, render_template
from .object_recognition import VisionAPI

routes = Blueprint('routes', __name__)
vision_api = VisionAPI()

@routes.route('/process', methods=['POST'])
def process_image():
    try:
        image_url = None
        
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                image_url = vision_api.upload_to_cloudinary(file)
                
        elif 'image_url' in request.form:
            image_url = request.form.get('image_url')
            
        if not image_url:
            return jsonify({"error": "No valid image provided"}), 400

        analysis_result = vision_api.analyze_image(image_url)
        
        return jsonify({
            "response": analysis_result,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/camera')
def camera():
    return render_template('camera.html')

@routes.route('/settings')
def settings():
    return render_template('settings.html')

@routes.route('/voice-commands')
def voice_commands():
    return render_template('voice_commands.html')