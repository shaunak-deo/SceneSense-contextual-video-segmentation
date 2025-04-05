import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from app.segmenter import process_video
from app.ad_search import search_ads_for_labels

# Get the base directory path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Create necessary directories
def setup_directories(app):
    """Create necessary directories for the application"""
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'app', 'output'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'app', 'static'), exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'mkv'}

# Create directories at startup
setup_directories(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed types: mp4, mov, avi, mkv'}), 400
    
    try:
        # Generate unique filename
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{os.urandom(4).hex()}{ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the video with a default chunk duration of 30 seconds
        segments = process_video(filepath, chunk_duration=30)
        
        # Read segments from output/labels.json
        labels_path = os.path.join(BASE_DIR, 'app', 'output', 'labels.json')
        with open(labels_path, 'r') as f:
            labeled_segments = json.load(f)
        
        # Add ads and frame paths to each segment
        for segment in labeled_segments:
            # Filter out generic labels and keep only specific ones
            specific_labels = []
            for label_group in segment.get('labels', []):
                specific_terms = [term.strip() for term in label_group.split(',') 
                                if len(term.strip().split()) <= 2 and term.strip()]
                if specific_terms:
                    specific_labels.extend(specific_terms[:2])
            
            # Get ads for the segment
            segment['ads'] = search_ads_for_labels(specific_labels[:3])
            
            # Add frame paths
            segment_id = segment.get('segment', 1)
            frame_dir = os.path.join(BASE_DIR, 'app', 'output', f"segment_{segment_id}")
            if os.path.exists(frame_dir):
                frame_files = [f for f in os.listdir(frame_dir) if f.endswith('.jpg')]
                if frame_files:
                    # Sort frames by name and get the last 3
                    frame_files.sort()
                    last_frames = frame_files[-3:]
                    segment['preview_frames'] = [f"/static/frames/segment_{segment_id}/{frame}" for frame in last_frames]
        
        # Clean up the uploaded video file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'segments': labeled_segments
        })
    except Exception as e:
        app.logger.error(f"Error processing video: {str(e)}")
        # Clean up the uploaded file if processing failed
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.route('/static/frames/<path:filename>')
def serve_frame(filename):
    """Serve frame images"""
    try:
        # Split the path to get segment directory and frame filename
        parts = filename.split('/')
        if len(parts) != 2:
            raise ValueError("Invalid frame path")
        
        segment_dir, frame_file = parts
        
        # Construct the correct path in the output directory
        frame_path = os.path.join(BASE_DIR, 'app', 'output', segment_dir, frame_file)
        app.logger.info(f"Serving frame from path: {frame_path}")
        
        if not os.path.exists(frame_path):
            app.logger.error(f"Frame not found: {frame_path}")
            return jsonify({'error': 'Frame not found'}), 404
            
        return send_file(frame_path, mimetype='image/jpeg')
    except Exception as e:
        app.logger.error(f"Error serving frame: {str(e)}")
        return jsonify({'error': f'Error serving frame: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 