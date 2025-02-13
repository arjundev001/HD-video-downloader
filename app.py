from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# Folder for storing the downloaded videos temporarily
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('video_url')
    quality = request.form.get('quality')

    if not video_url:
        return "Error: No URL provided", 400

    # Adjust format selection to avoid merging
    quality_formats = {
        "1080p": "bv*[height<=1080][ext=mp4]/b[ext=mp4]/best",
        "720p": "bv*[height<=720][ext=mp4]/b[ext=mp4]/best",
        "480p": "bv*[height<=480][ext=mp4]/b[ext=mp4]/best",
        "360p": "bv*[height<=360][ext=mp4]/b[ext=mp4]/best",
        "audio": "bestaudio[ext=m4a]"
    }

    selected_format = quality_formats.get(quality, "best")

    try:
        # Download settings for yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': selected_format
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)

        # Send file to user
        response = send_file(file_path, as_attachment=True)

        # Delete file after sending
        os.remove(file_path)

        return response

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
