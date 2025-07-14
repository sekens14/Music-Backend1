from flask import Flask, request, jsonify
from pytube import YouTube
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    format_type = data.get('format', 'mp3')  # mp3 or mp4
    
    try:
        yt = YouTube(url)
        
        if format_type == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()
            ext = 'mp3'
        else:
            stream = yt.streams.get_highest_resolution()
            ext = 'mp4'
            
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'title': yt.title,
            'duration': yt.length,
            'download_url': f"/downloads/{filename}"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/downloads/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)