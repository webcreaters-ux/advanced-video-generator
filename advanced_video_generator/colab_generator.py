"""
Simplified Colab Video Generator API
Easy-to-use interface for Google Colab
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from .main import AdvancedVideoGenerator, GenerationOptions, VideoQuality
from .cloud_manager import CloudManager

logger = logging.getLogger(__name__)


class ColabVideoGenerator:
    """Simplified video generator for Google Colab
    
    This class provides a simple API for generating videos from scripts
    without needing to manage complex configuration.
    
    Example:
        ```python
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
        ```
    """
    
    def __init__(self, 
                 output_dir: str = "./output",
                 temp_dir: str = "./temp",
                 quality: str = "medium",
                 tts_engine: str = "google",
                 language: str = "en-US"):
        """Initialize the Colab Video Generator
        
        Args:
            output_dir: Directory to save output videos
            temp_dir: Directory for temporary files
            quality: Default video quality (low, medium, high, ultra)
            tts_engine: TTS engine to use (google, edge, coqui, pyttsx3)
            language: Language for TTS (e.g., en-US, es-ES, fr-FR)
        """
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.default_quality = quality
        self.default_tts_engine = tts_engine
        self.default_language = language
        
        # Create directories
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize generator
        self._generator = None
        self._cloud = CloudManager()
        self._last_result = None
        
        # Quality mapping
        self._quality_map = {
            'low': VideoQuality.LOW,
            'medium': VideoQuality.MEDIUM,
            'high': VideoQuality.HIGH,
            'ultra': VideoQuality.ULTRA
        }
        
        print("🎬 ColabVideoGenerator initialized")
        print(f"   Output directory: {output_dir}")
        print(f"   Quality: {quality}")
        print(f"   TTS Engine: {tts_engine}")
    
    def _get_generator(self) -> AdvancedVideoGenerator:
        """Get or create the video generator"""
        if self._generator is None:
            # Create minimal config
            config = {
                'project': {
                    'output_dir': self.output_dir,
                    'temp_dir': self.temp_dir,
                    'log_dir': './logs'
                },
                'video': {
                    'resolution': '1920x1080',
                    'fps': 30,
                    'codec': 'libx264'
                },
                'text_to_speech': {
                    'engine': self.default_tts_engine,
                    'language': self.default_language,
                    'rate': 1.0
                },
                'image_generation': {
                    'model': 'stabilityai/stable-diffusion-2-1',
                    'steps': 25,
                    'guidance_scale': 7.5
                }
            }
            self._generator = AdvancedVideoGenerator()
            self._generator.config = config
        return self._generator
    
    def generate_from_script(self,
                            script_text: str,
                            output_name: str = "video.mp4",
                            quality: Optional[str] = None,
                            tts_engine: Optional[str] = None,
                            generate_images: bool = True,
                            add_subtitles: bool = True,
                            add_transitions: bool = True,
                            background_music: Optional[str] = None,
                            show_progress: bool = True) -> Dict[str, Any]:
        """Generate a video from script text
        
        Args:
            script_text: The script text to convert to video
            output_name: Name for the output video file
            quality: Video quality (low, medium, high, ultra)
            tts_engine: TTS engine to use
            generate_images: Whether to generate AI images
            add_subtitles: Whether to add subtitles
            add_transitions: Whether to add transitions
            background_music: Path to background music file
            show_progress: Whether to show progress messages
            
        Returns:
            Dictionary with generation results
        """
        if show_progress:
            print("🎬 Starting video generation...")
            print(f"   Script length: {len(script_text)} characters")
        
        # Get quality enum
        quality_enum = self._quality_map.get(
            quality or self.default_quality, 
            VideoQuality.MEDIUM
        )
        
        # Create options
        options = GenerationOptions(
            quality=quality_enum,
            generate_images=generate_images,
            add_subtitles=add_subtitles,
            add_transitions=add_transitions,
            voice_engine=tts_engine or self.default_tts_engine,
            add_background_music=bool(background_music),
            background_music_path=background_music
        )
        
        # Get generator
        generator = self._get_generator()
        
        # Generate video
        output_path = os.path.join(self.output_dir, output_name)
        
        if show_progress:
            print("📝 Processing script...")
        
        result = generator.generate_from_script(
            script_text=script_text,
            output_path=output_path,
            options=options
        )
        
        self._last_result = result
        
        if result['success']:
            if show_progress:
                print("✅ Video generated successfully!")
                print(f"   Duration: {result.get('duration', 0):.1f}s")
                print(f"   Output: {result['output_path']}")
        else:
            if show_progress:
                print(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    def generate_from_file(self,
                          script_file: str,
                          output_name: Optional[str] = None,
                          **kwargs) -> Dict[str, Any]:
        """Generate a video from a script file
        
        Args:
            script_file: Path to the script file
            output_name: Name for output (defaults to script filename)
            **kwargs: Additional arguments passed to generate_from_script
            
        Returns:
            Dictionary with generation results
        """
        # Read script file
        with open(script_file, 'r', encoding='utf-8') as f:
            script_text = f.read()
        
        # Default output name
        if output_name is None:
            output_name = Path(script_file).stem + ".mp4"
        
        return self.generate_from_script(
            script_text=script_text,
            output_name=output_name,
            **kwargs
        )
    
    def download_video(self, filename: Optional[str] = None):
        """Download the generated video in Colab
        
        Args:
            filename: Specific file to download (defaults to last generated)
        """
        try:
            from google.colab import files
            
            if filename:
                filepath = os.path.join(self.output_dir, filename)
            elif self._last_result and self._last_result.get('output_path'):
                filepath = self._last_result['output_path']
            else:
                print("❌ No video to download. Generate a video first.")
                return
            
            if os.path.exists(filepath):
                files.download(filepath)
                print(f"📥 Downloading: {filepath}")
            else:
                print(f"❌ File not found: {filepath}")
                
        except ImportError:
            print("❌ This function only works in Google Colab")
    
    def save_to_drive(self, 
                      filename: Optional[str] = None,
                      drive_folder: str = "VideoGenerator") -> bool:
        """Save the generated video to Google Drive
        
        Args:
            filename: Specific file to save (defaults to last generated)
            drive_folder: Folder name in Google Drive
            
        Returns:
            True if successful
        """
        try:
            if filename:
                filepath = os.path.join(self.output_dir, filename)
            elif self._last_result and self._last_result.get('output_path'):
                filepath = self._last_result['output_path']
            else:
                print("❌ No video to save. Generate a video first.")
                return False
            
            # Mount Google Drive
            self._cloud.mount_google_drive()
            
            # Save to Drive
            drive_path = f"/content/drive/MyDrive/{drive_folder}/{os.path.basename(filepath)}"
            success = self._cloud.save_to_drive(filepath, drive_path)
            
            if success:
                print(f"✅ Saved to Google Drive: {drive_path}")
            else:
                print("❌ Failed to save to Google Drive")
            
            return success
            
        except Exception as e:
            print(f"❌ Error saving to Drive: {e}")
            return False
    
    def list_videos(self) -> list:
        """List all generated videos
        
        Returns:
            List of video file paths
        """
        videos = []
        if os.path.exists(self.output_dir):
            for file in Path(self.output_dir).glob("*.mp4"):
                videos.append(str(file))
        return videos
    
    def get_video_info(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a generated video
        
        Args:
            filename: Video filename (defaults to last generated)
            
        Returns:
            Dictionary with video information
        """
        if filename:
            filepath = os.path.join(self.output_dir, filename)
        elif self._last_result and self._last_result.get('output_path'):
            filepath = self._last_result['output_path']
        else:
            return {"error": "No video specified"}
        
        if not os.path.exists(filepath):
            return {"error": f"File not found: {filepath}"}
        
        # Get file info
        stat = os.stat(filepath)
        
        return {
            "path": filepath,
            "size_mb": stat.st_size / (1024 * 1024),
            "created": stat.st_ctime,
            "modified": stat.st_mtime
        }
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir)
            print("🧹 Temporary files cleaned up")


# Convenience function for quick video generation
def quick_generate(script_text: str, 
                   output_name: str = "quick_video.mp4",
                   **kwargs) -> Dict[str, Any]:
    """Quickly generate a video from script text
    
    Args:
        script_text: The script to convert to video
        output_name: Output filename
        **kwargs: Additional arguments
        
    Returns:
        Generation result dictionary
    """
    generator = ColabVideoGenerator()
    return generator.generate_from_script(
        script_text=script_text,
        output_name=output_name,
        **kwargs
    )


__all__ = ['ColabVideoGenerator', 'quick_generate']
