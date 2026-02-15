"""
Auto Captions Extension
Automatic caption generation from audio
"""

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class AutoCaptions:
    """Generate automatic captions from audio"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize auto captions
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.language = self.config.get('language', 'en-US')
        self.model = None
    
    def load_model(self):
        """Load speech recognition model"""
        try:
            import speech_recognition as sr
            
            self.recognizer = sr.Recognizer()
            self._is_loaded = True
            logger.info("Speech recognition model loaded")
            
        except ImportError:
            logger.warning("speech_recognition not installed. Install with: pip install speechrecognition")
            self._is_loaded = False
    
    def generate_captions(self,
                         audio_file: str,
                         output_file: Optional[str] = None,
                         format: str = 'srt') -> Optional[str]:
        """Generate captions from audio file
        
        Args:
            audio_file: Path to audio file
            output_file: Output file path (optional)
            format: Caption format (srt, vtt, txt)
            
        Returns:
            Caption content or None
        """
        if not self._is_loaded:
            self.load_model()
        
        if not self._is_loaded or not hasattr(self, 'recognizer'):
            logger.error("Speech recognition not available")
            return None
        
        try:
            import speech_recognition as sr
            
            # Load audio
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech
            # Note: This uses Google API by default (requires internet)
            # For offline, use pocketsphinx
            text = self.recognizer.recognize_google(audio)
            
            # Generate timestamps (simplified)
            captions = self._generate_caption_segments(text, format)
            
            # Save to file if specified
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(captions)
                logger.info(f"Saved captions to: {output_file}")
            
            return captions
            
        except sr.UnknownValueError:
            logger.warning("Speech not recognized")
            return None
        except Exception as e:
            logger.error(f"Caption generation failed: {e}")
            return None
    
    def _generate_caption_segments(self, text: str, format: str) -> str:
        """Generate caption segments from text
        
        Args:
            text: Recognized text
            format: Output format
            
        Returns:
            Formatted captions
        """
        if format == 'srt':
            return self._to_srt(text)
        elif format == 'vtt':
            return self._to_vtt(text)
        else:
            return text
    
    def _to_srt(self, text: str) -> str:
        """Convert text to SRT format"""
        # Simplified - would need proper timing
        lines = text.split('. ')
        srt_output = ""
        
        for i, line in enumerate(lines, 1):
            start_time = self._format_srt_time(i * 3)  # 3 seconds per line
            end_time = self._format_srt_time((i + 1) * 3)
            
            srt_output += f"{i}\n"
            srt_output += f"{start_time} --> {end_time}\n"
            srt_output += f"{line.strip()}\n\n"
        
        return srt_output
    
    def _to_vtt(self, text: str) -> str:
        """Convert text to VTT format"""
        lines = text.split('. ')
        vtt_output = "WEBVTT\n\n"
        
        for i, line in enumerate(lines, 1):
            start_time = self._format_vtt_time(i * 3)
            end_time = self._format_vtt_time((i + 1) * 3)
            
            vtt_output += f"{i}\n"
            vtt_output += f"{start_time} --> {end_time}\n"
            vtt_output += f"{line.strip()}\n\n"
        
        return vtt_output
    
    def _format_srt_time(self, seconds: int) -> str:
        """Format time for SRT"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d},000"
    
    def _format_vtt_time(self, seconds: int) -> str:
        """Format time for VTT"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.000"
    
    def generate_from_video(self,
                          video_file: str,
                          output_file: Optional[str] = None) -> Optional[str]:
        """Generate captions directly from video
        
        Args:
            video_file: Path to video file
            output_file: Output file path
            
        Returns:
            Caption content
        """
        # Extract audio from video
        try:
            from moviepy.editor import VideoFileClip
            import tempfile
            import os
            
            # Load video
            video = VideoFileClip(video_file)
            
            # Extract audio to temp file
            audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
            video.audio.write_audiofile(audio_file, verbose=False, logger=None)
            video.close()
            
            # Generate captions
            captions = self.generate_captions(audio_file, output_file)
            
            # Cleanup
            os.unlink(audio_file)
            
            return captions
            
        except Exception as e:
            logger.error(f"Failed to generate captions from video: {e}")
            return None


def get_auto_captions(config: Optional[Dict[str, Any]] = None) -> AutoCaptions:
    """Get an AutoCaptions instance
    
    Args:
        config: Configuration dictionary
        
    Returns:
        AutoCaptions instance
    """
    return AutoCaptions(config)


__all__ = ['AutoCaptions', 'get_auto_captions']
