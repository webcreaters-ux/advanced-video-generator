"""
Advanced Video Generator
Generate professional videos from scripts using AI

Example usage:
    from advanced_video_generator import ColabVideoGenerator
    
    # Initialize generator
    generator = ColabVideoGenerator()
    
    # Generate video from script
    generator.generate_from_script(
        script_text="Your script here...",
        output_name="my_video.mp4",
        generate_images=True,
        add_subtitles=True
    )
"""

# Core components
from .main import (
    AdvancedVideoGenerator,
    GenerationOptions,
    VideoQuality,
    create_video_generator
)

# Simplified Colab interface
from .colab_generator import ColabVideoGenerator, quick_generate

# Configuration
from .config import ConfigManager, load_config

# Authentication
from .auth import (
    AuthManager,
    ClientCredentials,
    get_auth_manager,
    authenticate,
    is_authenticated
)

# TTS Generator
from .tts_generator import TTSGenerator, TTSConfig

# Version
__version__ = "1.0.0"
__author__ = "WebCreaters-UX"
__license__ = "MIT"

# Public API
__all__ = [
    # Main classes
    'AdvancedVideoGenerator',
    'GenerationOptions',
    'VideoQuality',
    'create_video_generator',
    
    # Colab interface
    'ColabVideoGenerator',
    'quick_generate',
    
    # Configuration
    'ConfigManager',
    'load_config',
    
    # Authentication
    'AuthManager',
    'ClientCredentials',
    'get_auth_manager',
    'authenticate',
    'is_authenticated',
    
    # TTS
    'TTSGenerator',
    'TTSConfig',
    
    # Metadata
    '__version__',
    '__author__',
    '__license__'
]
