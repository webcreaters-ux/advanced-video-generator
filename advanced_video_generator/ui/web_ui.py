"""
Web UI for Advanced Video Generator
Flask-based web interface for generating videos
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pathlib import Path

# Import the video generator
from ..main import AdvancedVideoGenerator, GenerationOptions, VideoQuality
from ..config import ConfigManager

logger = logging.getLogger(__name__)


class WebUI:
    """Web UI for video generation"""
    
    def __init__(self, config_path: str = None, host: str = "0.0.0.0", port: int = 5000):
        """Initialize web UI
        
        Args:
            config_path: Path to configuration file
            host: Host to bind to
            port: Port to bind to
        """
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.config_path = config_path
        self.generator = None
        
        # Configure upload folder
        self.upload_folder = "./uploads"
        self.output_folder = "./output"
        Path(self.upload_folder).mkdir(parents=True, exist_ok=True)
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
        
        # Configure Flask
        self.app.config['UPLOAD_FOLDER'] = self.upload_folder
        self.app.config['OUTPUT_FOLDER'] = self.output_folder
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
        
        # Setup routes
        self._setup_routes()
        
        # Setup CORS
        try:
            from flask_cors import CORS
            CORS(self.app)
        except ImportError:
            pass
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Render main page"""
            return render_template('index.html')
        
        @self.app.route('/api/generate', methods=['POST'])
        def generate():
            """Generate video from script"""
            try:
                data = request.get_json()
                
                script_text = data.get('script', '')
                quality = data.get('quality', 'medium')
                tts_engine = data.get('tts_engine', 'google')
                generate_images = data.get('generate_images', True)
                add_subtitles = data.get('add_subtitles', True)
                add_transitions = data.get('add_transitions', True)
                
                if not script_text:
                    return jsonify({'error': 'Script is required'}), 400
                
                # Initialize generator if needed
                if self.generator is None:
                    self.generator = AdvancedVideoGenerator(self.config_path)
                
                # Map quality
                quality_map = {
                    'low': VideoQuality.LOW,
                    'medium': VideoQuality.MEDIUM,
                    'high': VideoQuality.HIGH,
                    'ultra': VideoQuality.ULTRA
                }
                
                # Create options
                options = GenerationOptions(
                    quality=quality_map.get(quality, VideoQuality.MEDIUM),
                    generate_images=generate_images,
                    add_subtitles=add_subtitles,
                    add_transitions=add_transitions,
                    voice_engine=tts_engine
                )
                
                # Generate output filename
                import time
                output_name = f"video_{int(time.time())}.mp4"
                output_path = os.path.join(self.output_folder, output_name)
                
                # Generate video
                result = self.generator.generate_from_script(
                    script_text=script_text,
                    output_path=output_path,
                    options=options
                )
                
                if result['success']:
                    return jsonify({
                        'success': True,
                        'video_url': f"/api/download/{output_name}",
                        'duration': result.get('duration', 0),
                        'message': 'Video generated successfully!'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    }), 500
                    
            except Exception as e:
                logger.error(f"Generation error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/download/<filename>')
        def download(filename):
            """Download generated video"""
            try:
                filepath = os.path.join(self.output_folder, secure_filename(filename))
                if os.path.exists(filepath):
                    return send_file(filepath, as_attachment=True)
                return jsonify({'error': 'File not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/status')
        def status():
            """Check API status"""
            return jsonify({
                'status': 'online',
                'version': '1.0.0',
                'generator_ready': self.generator is not None
            })
    
    def run(self):
        """Run the web server"""
        logger.info(f"Starting web UI on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=True)


# Convenience function to run the web UI
def run_web_ui(config_path: str = None, host: str = "0.0.0.0", port: int = 5000):
    """Run the web UI
    
    Args:
        config_path: Path to configuration file
        host: Host to bind to
        port: Port to bind to
    """
    ui = WebUI(config_path, host, port)
    ui.run()


__all__ = ['WebUI', 'run_web_ui']
