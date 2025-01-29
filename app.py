from flask import Flask, request, jsonify, render_template
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_formats', methods=['POST'])
def get_formats():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL tidak boleh kosong'}), 400

    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            target_resolutions = {480, 720, 1080}
            resolution_map = {}

            # Ambil semua format video (termasuk tanpa audio)
            for fmt in formats:
                height = fmt.get('height')
                if height in target_resolutions and fmt.get('vcodec') != 'none':
                    key = f"{height}p"
                    if key not in resolution_map:
                        resolution_map[key] = {
                            'format_id': fmt['format_id'],
                            'has_audio': fmt.get('acodec') != 'none',
                            'ext': fmt.get('ext', 'mp4')
                        }

            # Konversi ke list dan tambahkan opsi "Terbaik"
            resolutions = [
                {
                    'resolution': res,
                    'format_id': details['format_id'],
                    'has_audio': details['has_audio'],
                    'ext': details['ext']
                } for res, details in resolution_map.items()
            ]

            # Urutkan dari resolusi tertinggi
            resolutions.sort(key=lambda x: int(x['resolution'].replace('p', '')), reverse=True)

            return jsonify({
                'resolutions': resolutions,
                'thumbnail': info.get('thumbnail', '')
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    format_id = data.get('format_id')

    # Gabungkan video + audio otomatis dengan FFmpeg
    ydl_opts = {
        'format': f'{format_id}+bestaudio/best',  # Prioritaskan format dengan audio
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'outtmpl': 'static/videos/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            return jsonify({'file_path': file_path})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('static/videos'):
        os.makedirs('static/videos')
    app.run(debug=True)