"""
Social Media Formats Extension
Export videos for TikTok, YouTube Shorts, Instagram, etc.
"""

import logging
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class SocialMediaFormats:
    """Export videos in social media formats"""
    
    # Format presets
    FORMATS = {
        'tiktok': {
            'name': 'TikTok',
            'resolution': (1080, 1920),  # 9:16 vertical
            'aspect_ratio': '9:16',
            'max_duration': 180,  # 3 minutes
            'fps': 30
        },
        'youtube_shorts': {
            'name': 'YouTube Shorts',
            'resolution': (1080, 1920),  # 9:16 vertical
            'aspect_ratio': '9:16',
            'max_duration': 60,  # 1 minute
            'fps': 30
        },
        'instagram_reel': {
            'name': 'Instagram Reel',
            'resolution': (1080, 1920),  # 9:16 vertical
            'aspect_ratio': '9:16',
            'max_duration': 90,  # 90 seconds
            'fps': 30
        },
        'instagram_story': {
            'name': 'Instagram Story',
            'resolution': (1080, 1920),  # 9:16 vertical
            'aspect_ratio': '9:16',
            'max_duration': 15,  # 15 seconds
            'fps': 30
        },
        'facebook_story': {
            'name': 'Facebook Story',
            'resolution': (1080, 1920),  # 9:16 vertical
            'aspect_ratio': '9:16',
            'max_duration': 20,  # 20 seconds
            'fps': 30
        },
        'twitter_video': {
            'name': 'Twitter/X Video',
            'resolution': (1280, 720),  # 16:9
            'aspect_ratio': '16:9',
            'max_duration': 140,  # 2:20
            'fps': 30
        },
        'linkedin_video': {
            'name': 'LinkedIn Video',
            'resolution': (1920, 1080),  # 16:9
            'aspect_ratio': '16:9',
            'max_duration': 600,  # 10 minutes
            'fps': 30
        },
        'square': {
            'name': 'Square (1:1)',
            'resolution': (1080, 1080),  # 1:1
            'aspect_ratio': '1:1',
            'max_duration': 600,
            'fps': 30
        },
        'landscape': {
            'name': 'Landscape (16:9)',
            'resolution': (1920, 1080),  # 16:9
            'aspect_ratio': '16:9',
            'max_duration': 600,
            'fps': 30
        },
        'portrait': {
            'name': 'Portrait (4:5)',
            'resolution': (1080, 1350),  # 4:5
            'aspect_ratio': '4:5',
            'max_duration': 600,
            'fps': 30
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize social media formats
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    def convert_format(self,
                      video_file: str,
                      output_file: str,
                      format_name: str,
                      quality: str = 'high') -> bool:
        """Convert video to social media format
        
        Args:
            video_file: Input video path
            output_file: Output video path
            format_name: Target format (tiktok, youtube_shorts, etc.)
            quality: Quality setting (low, medium, high)
            
        Returns:
            True if successful
        """
        if format_name not in self.FORMATS:
            logger.error(f"Unknown format: {format_name}")
            return False
        
        format_info = self.FORMATS[format_name]
        
        try:
            from moviepy.editor import VideoFileClip
            
            # Load video
            video = VideoFileClip(video_file)
            
            # Get target resolution
            target_width, target_height = format_info['resolution']
            
            # Resize video to target aspect ratio
            video = video.resize((target_width, target_height))
            
            # Apply quality settings
            if quality == 'low':
                bitrate = '1M'
            elif quality == 'medium':
                bitrate = '2.5M'
            else:  # high
                bitrate = '5M'
            
            # Write output
            import os
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            video.write_videofile(
                output_file,
                fps=format_info['fps'],
                codec='libx264',
                audio_codec='aac',
                bitrate=bitrate,
                verbose=False,
                logger=None
            )
            
            video.close()
            
            logger.info(f"Converted to {format_info['name']}: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to convert format: {e}")
            return False
    
    def convert_to_multiple(self,
                          video_file: str,
                          output_dir: str,
                          formats: list = None) -> Dict[str, str]:
        """Convert video to multiple formats
        
        Args:
            video_file: Input video path
            output_dir: Output directory
            formats: List of formats to convert to
            
        Returns:
            Dictionary of format -> output path
        """
        if formats is None:
            formats = ['tiktok', 'youtube_shorts', 'instagram_reel']
        
        results = {}
        
        for format_name in formats:
            output_file = f"{output_dir}/{format_name}_{video_file}"
            success = self.convert_format(video_file, output_file, format_name)
            
            if success:
                results[format_name] = output_file
        
        return results
    
    def get_format_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a format
        
        Args:
            format_name: Format name
            
        Returns:
            Format information dictionary
        """
        return self.FORMATS.get(format_name)
    
    def list_formats(self) -> Dict[str, Dict[str, Any]]:
        """List all available formats
        
        Returns:
            Dictionary of format information
        """
        return self.FORMATS.copy()
    
    def suggest_format(self, platform: str) -> str:
        """Suggest best format for a platform
        
        Args:
            platform: Platform name
            
        Returns:
            Recommended format name
        """
        suggestions = {
            'tiktok': 'tiktok',
            'youtube': 'youtube_shorts',
            'youtube shorts': 'youtube_shorts',
            'instagram': 'instagram_reel',
            'instagram reel': 'instagram_reel',
            'instagram story': 'instagram_story',
            'facebook': 'facebook_story',
            'twitter': 'twitter_video',
            'x': 'twitter_video',
            'linkedin': 'linkedin_video'
        }
        
        return suggestions.get(platform.lower(), 'landscape')


def get_social_media_formats(config: Optional[Dict[str, Any]] = None) -> SocialMediaFormats:
    """Get a SocialMediaFormats instance
    
    Args:
        config: Configuration dictionary
        
    Returns:
        SocialMediaFormats instance
    """
    return SocialMediaFormats(config)


__all__ = ['SocialMediaFormats', 'get_social_media_formats']
