#!/usr/bin/env python3
"""
Advanced Video Generator - Main Entry Point
Command line interface and web server
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from advanced_video_generator import (
    AdvancedVideoGenerator,
    GenerationOptions,
    VideoQuality,
    create_video_generator
)
from advanced_video_generator.config import ConfigManager
from advanced_video_generator.utils import setup_logging

logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Advanced Video Generator - Create videos from scripts using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --script my_script.txt --output video.mp4
  %(prog)s --web-ui
  %(prog)s --batch --script-dir ./scripts
  %(prog)s --install-extension auto_captions
        """
    )
    
    # Input/output
    parser.add_argument('--script', type=str, 
                       help='Script file to process')
    parser.add_argument('--output', type=str, default='output/video.mp4',
                       help='Output video file (default: output/video.mp4)')
    parser.add_argument('--config', type=str,
                       help='Configuration file path')
    
    # Generation options
    parser.add_argument('--quality', type=str, 
                       choices=['low', 'medium', 'high', 'ultra'],
                       default='medium',
                       help='Video quality (default: medium)')
    parser.add_argument('--no-images', action='store_true',
                       help='Skip AI image generation')
    parser.add_argument('--no-subtitles', action='store_true',
                       help='Skip subtitle generation')
    parser.add_argument('--tts-engine', type=str,
                       choices=['google', 'edge', 'coqui', 'pyttsx3'],
                       default='google',
                       help='TTS engine to use (default: google)')
    parser.add_argument('--background-music', type=str,
                       help='Path to background music file')
    
    # Batch processing
    parser.add_argument('--batch', action='store_true',
                       help='Batch process multiple scripts')
    parser.add_argument('--script-dir', type=str,
                       help='Directory containing script files')
    parser.add_argument('--output-dir', type=str, default='output',
                       help='Output directory for batch processing')
    
    # Extensions
    parser.add_argument('--install-extension', type=str,
                       help='Install extension (voice_cloning, auto_captions, etc.)')
    parser.add_argument('--list-extensions', action='store_true',
                       help='List available extensions')
    
    # UI modes
    parser.add_argument('--web-ui', action='store_true',
                       help='Start web UI server')
    parser.add_argument('--colab', action='store_true',
                       help='Run in Colab mode')
    parser.add_argument('--cli', action='store_true',
                       help='Run in command line mode (default)')
    
    # System
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--version', action='store_true',
                       help='Show version information')
    
    return parser.parse_args()

def show_version():
    """Show version information"""
    import pkg_resources
    try:
        version = pkg_resources.get_distribution("advanced-video-generator").version
    except:
        version = "1.0.0 (development)"
    
    print(f"Advanced Video Generator v{version}")
    print("https://github.com/yourusername/advanced-video-generator")

def list_extensions():
    """List available extensions"""
    extensions = {
        'voice_cloning': {
            'name': 'Voice Cloning',
            'description': 'Clone voices for custom TTS',
            'dependencies': ['TTS', 'torchaudio'],
            'enabled_by_default': False
        },
        'advanced_transitions': {
            'name': 'Advanced Transitions',
            'description': '50+ transition effects',
            'dependencies': ['opencv-python', 'scipy'],
            'enabled_by_default': False
        },
        'auto_captions': {
            'name': 'Auto Captions',
            'description': 'Automatic caption generation from audio',
            'dependencies': ['speech_recognition', 'pydub'],
            'enabled_by_default': False
        },
        'social_media_formats': {
            'name': 'Social Media Formats',
            'description': 'Export for TikTok, YouTube Shorts, Instagram',
            'dependencies': [],
            'enabled_by_default': False
        },
        'video_analytics': {
            'name': 'Video Analytics',
            'description': 'Analyze video performance and engagement',
            'dependencies': ['pandas', 'matplotlib'],
            'enabled_by_default': False
        }
    }
    
    print("Available Extensions:")
    print("=" * 60)
    for key, ext in extensions.items():
        print(f"\n{key}:")
        print(f"  Name: {ext['name']}")
        print(f"  Description: {ext['description']}")
        print(f"  Dependencies: {', '.join(ext['dependencies'])}")
        print(f"  Enabled by default: {ext['enabled_by_default']}")

def install_extension(extension_name: str):
    """Install an extension"""
    import subprocess
    
    extension_deps = {
        'voice_cloning': ['TTS', 'torchaudio'],
        'advanced_transitions': ['opencv-python', 'scipy'],
        'auto_captions': ['speechrecognition', 'pydub'],
        'social_media_formats': [],
        'video_analytics': ['pandas', 'matplotlib']
    }
    
    if extension_name not in extension_deps:
        print(f"Unknown extension: {extension_name}")
        return False
    
    print(f"Installing {extension_name}...")
    
    # Install dependencies
    deps = extension_deps[extension_name]
    for dep in deps:
        print(f"  Installing {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"    ✅ {dep} installed")
        except subprocess.CalledProcessError:
            print(f"    ❌ Failed to install {dep}")
            return False
    
    # Update config to enable extension
    config_path = "config.yaml"
    if os.path.exists(config_path):
        config = ConfigManager.load_config(config_path)
    else:
        config = ConfigManager.load_config()
    
    config['extensions'][extension_name] = True
    ConfigManager.save_config(config, config_path)
    
    print(f"\n✅ Extension '{extension_name}' installed and enabled!")
    print(f"   Restart the application to use the extension.")
    
    return True

def generate_single_video(args, generator: AdvancedVideoGenerator):
    """Generate a single video"""
    if not args.script or not os.path.exists(args.script):
        print(f"Error: Script file not found: {args.script}")
        return False
    
    # Read script
    with open(args.script, 'r', encoding='utf-8') as f:
        script_text = f.read()
    
    # Create output directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Create generation options
    quality_map = {
        'low': VideoQuality.LOW,
        'medium': VideoQuality.MEDIUM,
        'high': VideoQuality.HIGH,
        'ultra': VideoQuality.ULTRA
    }
    
    options = GenerationOptions(
        quality=quality_map[args.quality],
        generate_images=not args.no_images,
        add_subtitles=not args.no_subtitles,
        voice_engine=args.tts_engine,
        add_background_music=bool(args.background_music),
        background_music_path=args.background_music
    )
    
    # Generate video
    print(f"Generating video from: {args.script}")
    print(f"Output: {args.output}")
    print(f"Options: {options}")
    print("-" * 50)
    
    result = generator.generate_from_script(
        script_text=script_text,
        output_path=args.output,
        options=options
    )
    
    if result['success']:
        print(f"\n✅ Video generated successfully!")
        print(f"   Duration: {result['duration']:.1f}s")
        print(f"   Generation time: {result['generation_time']:.1f}s")
        print(f"   Output: {result['output_path']}")
        return True
    else:
        print(f"\n❌ Video generation failed:")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return False

def batch_generate(args, generator: AdvancedVideoGenerator):
    """Batch generate videos"""
    if not args.script_dir or not os.path.isdir(args.script_dir):
        print(f"Error: Script directory not found: {args.script_dir}")
        return False
    
    # Find script files
    script_files = []
    for ext in ['.txt', '.md', '.script']:
        script_files.extend(Path(args.script_dir).glob(f"*{ext}"))
    
    if not script_files:
        print(f"No script files found in {args.script_dir}")
        return False
    
    print(f"Found {len(script_files)} script files")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Create generation options
    quality_map = {
        'low': VideoQuality.LOW,
        'medium': VideoQuality.MEDIUM,
        'high': VideoQuality.HIGH,
        'ultra': VideoQuality.ULTRA
    }
    
    options = GenerationOptions(
        quality=quality_map[args.quality],
        generate_images=not args.no_images,
        add_subtitles=not args.no_subtitles,
        voice_engine=args.tts_engine
    )
    
    # Process each script
    results = {}
    for script_file in script_files:
        print(f"\nProcessing: {script_file.name}")
        
        with open(script_file, 'r', encoding='utf-8') as f:
            script_text = f.read()
        
        output_path = os.path.join(
            args.output_dir,
            f"{script_file.stem}.mp4"
        )
        
        result = generator.generate_from_script(
            script_text=script_text,
            output_path=output_path,
            options=options
        )
        
        results[script_file.name] = result
        
        if result['success']:
            print(f"  ✅ Success: {output_path}")
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("Batch Processing Summary")
    print("=" * 50)
    
    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"Total scripts: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success rate: {(successful/total*100):.1f}%")
    
    return successful > 0

def start_web_ui():
    """Start web UI server"""
    try:
        from advanced_video_generator.ui.web_ui import WebUI
        
        print("Starting Web UI...")
        print("Open your browser and navigate to: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        
        ui = WebUI()
        ui.run()
        
    except ImportError as e:
        print(f"Error: {e}")
        print("Install Flask to use the web UI:")
        print("  pip install flask flask-cors")
        return False
    except KeyboardInterrupt:
        print("\nWeb UI stopped")
        return True

def main():
    """Main function"""
    args = parse_arguments()
    
    # Show version
    if args.version:
        show_version()
        return
    
    # List extensions
    if args.list_extensions:
        list_extensions()
        return
    
    # Install extension
    if args.install_extension:
        install_extension(args.install_extension)
        return
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)
    
    # Load configuration
    config = ConfigManager.load_config(args.config)
    
    # Validate config
    is_valid, errors = ConfigManager.validate_config(config)
    if not is_valid:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return
    
    # Create generator
    try:
        generator = create_video_generator(args.config)
    except Exception as e:
        print(f"Failed to initialize video generator: {e}")
        return
    
    # Run in appropriate mode
    if args.web_ui:
        start_web_ui()
    elif args.batch:
        batch_generate(args, generator)
    elif args.script:
        generate_single_video(args, generator)
    else:
        # Default to CLI mode with interactive prompts
        print("Advanced Video Generator - Interactive Mode")
        print("=" * 50)
        
        script_path = input("Enter script file path: ").strip()
        if not script_path:
            print("No script file provided")
            return
        
        output_path = input("Enter output file path [output/video.mp4]: ").strip()
        if not output_path:
            output_path = "output/video.mp4"
        
        args.script = script_path
        args.output = output_path
        
        generate_single_video(args, generator)

if __name__ == "__main__":
    main()
