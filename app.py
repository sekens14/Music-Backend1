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
    return "YouTube Downloader Backend is Running"

@app.route('/download', methods=['POST'])
def download_video():
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

@app.route('/downloads/<filename>', methods=['GET'])
def serve_file(filename):
    try:
        return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'File not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)