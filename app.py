from flask import Flask, request, jsonify, send_from_directory
import json
import os
import glob
from flask_cors import CORS
import yt_dlp
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Data file path
DATA_FILE = "youtube.txt"

def load_data():
    """Load videos from the data file"""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_data(videos):
    """Save videos to the data file"""
    with open(DATA_FILE, "w") as file:
        json.dump(videos, file, indent=2)

def extract_video_info(url):
    """Extract video information from YouTube URL"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if not info:
                raise Exception("Failed to extract video information - no data returned")

            # Get video title
            title = info.get('title', 'Unknown Title') if info else 'Unknown Title'

            # Get duration in minutes
            duration_seconds = info.get('duration', 0) if info else 0
            duration_minutes = round(duration_seconds / 60) if duration_seconds else 0

            return {
                'title': title,
                'duration': duration_minutes,
                'video_id': info.get('id', '') if info else '',
                'url': url
            }
    except Exception as e:
        raise Exception(f"Failed to extract video info: {str(e)}")

def download_video(url, quality='best', output_path='./downloads'):
    """Download video from YouTube URL with simple approach"""
    try:
        # Create downloads directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        # Use the most basic format selection that works with all videos
        ydl_opts = {
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'format': 'mp4/best[height<=480]/best[height<=720]/best',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            # Try MP4 first, then lower resolutions, then best available
            # This should work with virtually all YouTube videos
        }

        print(f"Starting download from: {url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first to get the title
            info = ydl.extract_info(url, download=False)

            if not info:
                raise Exception("Could not extract video information")

            # Now download with the same options
            info = ydl.extract_info(url, download=True)

            # Get the expected filename
            expected_filename = ydl.prepare_filename(info)

            # Check for the file with various extensions
            possible_extensions = ['.mp4', '.webm', '.m4a', '.mp3', '.mkv', '.avi', '.flv']
            base_filename = expected_filename.rsplit('.', 1)[0] if '.' in expected_filename else expected_filename

            for ext in possible_extensions:
                possible_file = base_filename + ext
                if os.path.exists(possible_file):
                    print(f"Download successful: {possible_file}")
                    return possible_file

            # If still not found, look for any file with the video title
            title = (info.get('title', 'Unknown') if info else 'Unknown').replace('/', '_').replace('\\', '_').replace(' ', '*')
            pattern = f"{output_path}/*{title}*"
            matches = glob.glob(pattern)
            if matches:
                print(f"Found by title pattern: {matches[0]}")
                return matches[0]

            raise Exception(f"Download completed but file not found. Expected: {expected_filename}")

    except Exception as e:
        error_msg = str(e)
        print(f"Download error: {error_msg}")
        raise Exception(f"Failed to download video: {error_msg}")

def is_valid_youtube_url(url):
    """Check if URL is a valid YouTube URL"""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)'
        r'[a-zA-Z0-9_-]{11}'
    )
    return re.match(youtube_regex, url) is not None

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'ytmanager.html')

@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Get all videos"""
    try:
        videos = load_data()
        return jsonify({
            'success': True,
            'videos': videos,
            'total': len(videos)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/videos', methods=['POST'])
def add_video():
    """Add a new video"""
    try:
        data = request.get_json()
        if not data or 'video' not in data or 'time' not in data:
            return jsonify({
                'success': False,
                'error': 'Video name and time are required'
            }), 400

        videos = load_data()
        new_video = {
            'video': data['video'].strip(),
            'time': data['time'].strip()
        }

        if not new_video['video'] or not new_video['time']:
            return jsonify({
                'success': False,
                'error': 'Video name and time cannot be empty'
            }), 400

        videos.append(new_video)
        save_data(videos)

        return jsonify({
            'success': True,
            'message': 'Video added successfully',
            'video': new_video
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/videos/<int:index>', methods=['PUT'])
def update_video(index):
    """Update a video by index"""
    try:
        data = request.get_json()
        if not data or 'video' not in data or 'time' not in data:
            return jsonify({
                'success': False,
                'error': 'Video name and time are required'
            }), 400

        videos = load_data()

        if index < 0 or index >= len(videos):
            return jsonify({
                'success': False,
                'error': 'Invalid video index'
            }), 404

        updated_video = {
            'video': data['video'].strip(),
            'time': data['time'].strip()
        }

        if not updated_video['video'] or not updated_video['time']:
            return jsonify({
                'success': False,
                'error': 'Video name and time cannot be empty'
            }), 400

        videos[index] = updated_video
        save_data(videos)

        return jsonify({
            'success': True,
            'message': 'Video updated successfully',
            'video': updated_video
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/videos/<int:index>', methods=['DELETE'])
def delete_video(index):
    """Delete a video by index"""
    try:
        videos = load_data()

        if index < 0 or index >= len(videos):
            return jsonify({
                'success': False,
                'error': 'Invalid video index'
            }), 404

        deleted_video = videos.pop(index)
        save_data(videos)

        return jsonify({
            'success': True,
            'message': 'Video deleted successfully',
            'video': deleted_video
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download', methods=['POST'])
def download_youtube_video():
    """Download a video from YouTube URL and add to collection"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'YouTube URL is required'
            }), 400

        url = data['url'].strip()
        quality = data.get('quality', 'best[height<=720]')  # Default quality
        action = data.get('action', 'download')  # Default action is download

        if not url:
            return jsonify({
                'success': False,
                'error': 'URL cannot be empty'
            }), 400

        # Validate YouTube URL
        if not is_valid_youtube_url(url):
            return jsonify({
                'success': False,
                'error': 'Invalid YouTube URL format'
            }), 400

        # Extract video information and download
        try:
            video_info = extract_video_info(url)
        except:
            # If info extraction fails, use fallback values
            video_info = {
                'title': f'Downloaded Video ({url.split("=")[-1][:10] if "=" in url else "Unknown"})',
                'duration': 0,
                'video_id': url.split("=")[-1][:11] if "=" in url else '',
            }

        # Download the video with selected quality
        download_path = download_video(url, quality)

        # Add to video collection
        videos = load_data()
        new_video = {
            'video': video_info['title'],
            'time': str(video_info['duration']),
            'url': url,
            'download_path': download_path,
            'video_id': video_info['video_id'],
            'quality': quality
        }

        videos.append(new_video)
        save_data(videos)

        return jsonify({
            'success': True,
            'message': 'Video downloaded and added successfully!',
            'video': new_video,
            'download_path': download_path
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to download video: {str(e)}'
        }), 500

@app.route('/downloads')
def list_downloads():
    """List files in the downloads directory"""
    try:
        if not os.path.exists('downloads'):
            return jsonify({'error': 'Downloads directory not found'}), 404

        files = []
        for filename in os.listdir('downloads'):
            filepath = os.path.join('downloads', filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'url': f'/downloads/{filename}'
                })

        return jsonify({'files': files, 'total': len(files)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloads/<filename>')
def serve_download_file(filename):
    """Serve individual download file"""
    try:
        return send_from_directory('downloads', filename, as_attachment=False)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about videos"""
    try:
        videos = load_data()
        total_videos = len(videos)
        total_duration = 0

        for video in videos:
            time_str = video.get('time', '0')
            # Handle time strings with 'min' suffix or just numbers
            if isinstance(time_str, str):
                time_str = time_str.replace('min', '').strip()
            try:
                total_duration += int(time_str)
            except (ValueError, TypeError):
                continue  # Skip invalid entries

        return jsonify({
            'success': True,
            'stats': {
                'total_videos': total_videos,
                'total_duration': total_duration
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting YouTube Video Manager Server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⚡ Server is running...")
    app.run(debug=True, host='0.0.0.0', port=5000)
