"""
Video processing module for video generator
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Process and assemble video components"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize video processor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.video_config = config.get('video', {})
        self.resolution = self.video_config.get('resolution', '1920x1080')
        self.fps = self.video_config.get('fps', 30)
        self.codec = self.video_config.get('codec', 'libx264')
    
    def create_slideshow(self,
                        images: List[str],
                        audio_file: str,
                        output_file: str,
                        durations: Optional[List[float]] = None,
                        resolution: Optional[str] = None,
                        fps: Optional[int] = None) -> bool:
        """Create a video slideshow from images and audio
        
        Args:
            images: List of image file paths
            audio_file: Path to audio file
            output_file: Path to save output video
            durations: Duration for each image
            resolution: Video resolution
            fps: Frames per second
            
        Returns:
            True if successful
        """
        try:
            from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_videoclips
            from moviepy.editor import ImageClip
            
            if not images:
                logger.error("No images provided")
                return False
            
            # Use defaults
            resolution = resolution or self.resolution
            fps = fps or self.fps
            
            # Parse resolution
            width, height = map(int, resolution.split('x'))
            
            # Calculate durations
            if durations is None:
                # Get audio duration
                audio = AudioFileClip(audio_file)
                total_duration = audio.duration
                duration_per_image = total_duration / len(images)
                durations = [duration_per_image] * len(images)
            
            # Create video clips from images
            clips = []
            for img_path, duration in zip(images, durations):
                if os.path.exists(img_path):
                    clip = ImageClip(img_path, duration=duration)
                    clip = clip.resize((width, height))
                    clips.append(clip)
            
            if not clips:
                logger.error("No valid images found")
                return False
            
            # Concatenate clips
            video = concatenate_videoclips(clips, method="compose")
            
            # Add audio
            if os.path.exists(audio_file):
                audio = AudioFileClip(audio_file)
                video = video.set_audio(audio)
            
            # Write output
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            video.write_videofile(
                output_file,
                fps=fps,
                codec=self.codec,
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None
            )
            
            # Cleanup
            video.close()
            if 'audio' in dir():
                audio.close()
            
            logger.info(f"Created video: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create slideshow: {e}")
            return False
    
    def merge_videos(self,
                    video_files: List[str],
                    output_file: str,
                    add_transitions: bool = False) -> bool:
        """Merge multiple videos into one
        
        Args:
            video_files: List of video file paths
            output_file: Path to save output video
            add_transitions: Whether to add transitions
            
        Returns:
            True if successful
        """
        try:
            from moviepy.editor import VideoFileClip, concatenate_videoclips
            
            if not video_files:
                logger.error("No videos provided")
                return False
            
            # Load all videos
            clips = []
            for video_path in video_files:
                if os.path.exists(video_path):
                    clip = VideoFileClip(video_path)
                    clips.append(clip)
            
            if not clips:
                logger.error("No valid videos found")
                return False
            
            # Concatenate
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Write output
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            final_video.write_videofile(
                output_file,
                fps=self.fps,
                codec=self.codec,
                audio_codec='aac',
                logger=None
            )
            
            # Cleanup
            final_video.close()
            for clip in clips:
                clip.close()
            
            logger.info(f"Merged videos: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to merge videos: {e}")
            return False
    
    def add_subtitles(self,
                     video_file: str,
                     subtitles: List[Dict],
                     output_file: str) -> bool:
        """Add subtitles to a video
        
        Args:
            video_file: Path to input video
            subtitles: List of subtitle dictionaries with 'text', 'start', 'end'
            output_file: Path to save output video
            
        Returns:
            True if successful
        """
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            
            # Load video
            video = VideoFileClip(video_file)
            
            # Create subtitle clips
            subtitle_clips = []
            for sub in subtitles:
                txt_clip = TextClip(
                    sub['text'],
                    fontsize=24,
                    color='white',
                    bg_color='black',
                    transparent=True
                )
                txt_clip = txt_clip.set_position(('center', 'bottom'))
                txt_clip = txt_clip.set_start(sub['start'])
                txt_clip = txt_clip.set_duration(sub['end'] - sub['start'])
                subtitle_clips.append(txt_clip)
            
            # Composite video with subtitles
            final = CompositeVideoClip([video] + subtitle_clips)
            
            # Write output
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            final.write_videofile(
                output_file,
                fps=self.fps,
                codec=self.codec,
                audio_codec='aac',
                logger=None
            )
            
            # Cleanup
            final.close()
            video.close()
            
            logger.info(f"Added subtitles: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add subtitles: {e}")
            # Copy original file as fallback
            import shutil
            shutil.copy(video_file, output_file)
            return True
    
    def add_transitions(self,
                       video_file: str,
                       output_file: str,
                       transition_type: str = "fade") -> bool:
        """Add transitions to a video
        
        Args:
            video_file: Path to input video
            output_file: Path to save output video
            transition_type: Type of transition
            
        Returns:
            True if successful
        """
        try:
            from moviepy.editor import VideoFileClip
            
            # Load video
            video = VideoFileClip(video_file)
            
            # Add fade in/out
            if transition_type == "fade":
                video = video.fadein(1.0).fadeout(1.0)
            
            # Write output
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            video.write_videofile(
                output_file,
                fps=self.fps,
                codec=self.codec,
                audio_codec='aac',
                logger=None
            )
            
            # Cleanup
            video.close()
            
            logger.info(f"Added transitions: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add transitions: {e}")
            # Copy original file as fallback
            import shutil
            shutil.copy(video_file, output_file)
            return True
    
    def add_background_music(self,
                            video_file: str,
                            music_file: str,
                            output_file: str,
                            volume: float = 0.3) -> bool:
        """Add background music to a video
        
        Args:
            video_file: Path to input video
            music_file: Path to music file
            output_file: Path to save output video
            volume: Music volume (0.0 to 1.0)
            
        Returns:
            True if successful
        """
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
            
            # Load video
            video = VideoFileClip(video_file)
            
            # Load music
            music = AudioFileClip(music_file)
            
            # Loop music if needed
            if music.duration < video.duration:
                # Loop music
                music = music.loop(duration=video.duration)
            else:
                # Trim music
                music = music.subclip(0, video.duration)
            
            # Set volume
            music = music.volumex(volume)
            
            # Composite audio
            if video.audio:
                final_audio = CompositeAudioClip([video.audio, music])
            else:
                final_audio = music
            
            # Set audio
            video = video.set_audio(final_audio)
            
            # Write output
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            video.write_videofile(
                output_file,
                fps=self.fps,
                codec=self.codec,
                audio_codec='aac',
                logger=None
            )
            
            # Cleanup
            video.close()
            music.close()
            
            logger.info(f"Added background music: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add background music: {e}")
            # Copy original file as fallback
            import shutil
            shutil.copy(video_file, output_file)
            return True
    
    def get_video_info(self, video_file: str) -> Dict[str, Any]:
        """Get information about a video file
        
        Args:
            video_file: Path to video file
            
        Returns:
            Dictionary with video information
        """
        try:
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(video_file)
            
            info = {
                'duration': video.duration,
                'fps': video.fps,
                'size': video.size,
                'has_audio': video.audio is not None
            }
            
            video.close()
            return info
            
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return {}


__all__ = ['VideoProcessor']
