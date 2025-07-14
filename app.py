from flask import Flask, request, jsonify, send_from_directory
from pytube import YouTube
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Add root route
@app.route('/')
def home():
    return "YouTube Downloader Backend is Running",200

@app.route('/download', methods=['POST'])
def download_video():
    @app.route('/download', methods=['POST'])
def download_video():
    try:
        # Ensure JSON was received
        if not request.is_json:
            return {"error": "Request must be JSON"}, 400
            
        data = request.get_json()
        
        # Validate required fields
        if 'url' not in data:
            return {"error": "Missing 'url' parameter"}, 400
            
        url = data['url']
        format_type = data.get('format', 'mp3')

        # Initialize YouTube with error handling
        try:
            yt = YouTube(url)
            yt.bypass_age_gate()  # Bypass age restrictions
        except Exception as e:
            return {"error": f"YouTube initialization failed: {str(e)}"}, 400

        # Stream selection with validation
        stream = yt.streams.filter(only_audio=True).first() if format_type == 'mp3' else yt.streams.get_highest_resolution()
        if not stream:
            return {"error": "No suitable stream found"}, 400

        # Download with error handling
        try:
            filename = f"{uuid.uuid4()}.{format_type}"
            stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
            return {
                "success": True,
                "filename": filename,
                "title": yt.title
            }
        except Exception as e:
            return {"error": f"Download failed: {str(e)}"}, 500

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}, 500
    data = request.get_json()  # Changed from request.json for better compatibility
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data received'}), 400
        
    url = data.get('url')
    format_type = data.get('format', 'mp3')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    try:
        yt = YouTube(url)
        
        if format_type == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()
            ext = 'mp3'
        else:
            stream = yt.streams.get_highest_resolution()
            ext = 'mp4'
            
        filename = f"{uuid.uuid4()}.{ext}"
        stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'title': yt.title,
            'duration': yt.length,
            'download_url': f"/downloads/{filename}"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/debug')
def debug():
    return {
        "status": "online",
        "pytube_version": YouTube.__version__,
        "downloads_folder_exists": os.path.exists(DOWNLOAD_FOLDER)
    }