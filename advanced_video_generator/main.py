#!/usr/bin/env python3
"""
Advanced Video Generator - Main Module
Complete video generation pipeline with AI integration
"""

import os
import sys
import json
import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from .tts_generator import TTSGenerator
from .image_generator import ImageGenerator
from .video_processor import VideoProcessor
from .script_processor import ScriptProcessor
from .cloud_manager import CloudManager
from .config import ConfigManager
from .utils import setup_logging, Timer, ProgressTracker

logger = logging.getLogger(__name__)

class VideoQuality(Enum):
    """Video quality presets"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class GenerationOptions:
    """Options for video generation"""
    quality: VideoQuality = VideoQuality.MEDIUM
    generate_images: bool = True
    add_subtitles: bool = True
    add_transitions: bool = True
    add_background_music: bool = False
    background_music_path: Optional[str] = None
    voice_engine: str = "google"
    image_engine: str = "stable_diffusion"
    output_format: str = "mp4"
    chunk_duration: int = 300  # seconds
    parallel_processing: bool = True
    max_workers: int = 4
    save_to_cloud: bool = False
    cloud_provider: str = "google_drive"
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GenerationOptions':
        """Create options from dictionary"""
        return cls(**data)

class AdvancedVideoGenerator:
    """Main video generation class"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the video generator
        
        Args:
            config_path: Path to configuration file
        """
        self.config = ConfigManager.load_config(config_path)
        self.options = GenerationOptions()
        
        # Setup components
        self.tts = TTSGenerator(self.config)
        self.images = ImageGenerator(self.config)
        self.video = VideoProcessor(self.config)
        self.script = ScriptProcessor(self.config)
        self.cloud = CloudManager(self.config)
        
        # Setup directories
        self._setup_directories()
        
        # Setup logging
        setup_logging(self.config['project']['log_dir'])
        
        # Statistics
        self.stats = {
            'total_videos': 0,
            'total_duration': 0,
            'success_rate': 0.0,
            'average_generation_time': 0.0
        }
        
        logger.info("Advanced Video Generator initialized")
    
    def _setup_directories(self):
        """Create necessary directories"""
        project_config = self.config['project']
        
        directories = [
            project_config['output_dir'],
            project_config['temp_dir'],
            project_config['log_dir'],
            project_config.get('cache_dir', './cache'),
            project_config.get('models_dir', './models')
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    def generate_from_script(self, script_text: str, 
                           output_path: str,
                           options: Optional[GenerationOptions] = None) -> Dict[str, Any]:
        """Generate video from script text
        
        Args:
            script_text: The script to convert to video
            output_path: Path to save the output video
            options: Generation options (uses default if None)
            
        Returns:
            Dictionary with generation results
        """
        if options is None:
            options = self.options
        
        logger.info(f"Starting video generation: {output_path}")
        timer = Timer()
        
        try:
            # Step 1: Process script
            logger.info("Step 1: Processing script...")
            chunks = self.script.parse_script(
                script_text, 
                max_chunk_duration=options.chunk_duration
            )
            
            logger.info(f"Script parsed into {len(chunks)} chunks")
            
            # Step 2: Generate audio
            logger.info("Step 2: Generating audio...")
            audio_files = self._generate_audio_for_chunks(chunks, options)
            
            if not audio_files:
                raise ValueError("Audio generation failed")
            
            # Step 3: Generate images (if enabled)
            image_files = []
            if options.generate_images:
                logger.info("Step 3: Generating images...")
                image_files = self._generate_images_for_chunks(chunks, options)
            
            # Step 4: Create video chunks
            logger.info("Step 4: Creating video chunks...")
            video_chunks = self._create_video_chunks(
                chunks, audio_files, image_files, options
            )
            
            if not video_chunks:
                raise ValueError("Video chunk creation failed")
            
            # Step 5: Merge chunks
            logger.info("Step 5: Merging video chunks...")
            success = self._merge_video_chunks(video_chunks, output_path)
            
            if not success:
                raise ValueError("Video merging failed")
            
            # Step 6: Add enhancements
            logger.info("Step 6: Adding enhancements...")
            final_video = self._enhance_video(output_path, chunks, options)
            
            # Step 7: Save to cloud (if enabled)
            if options.save_to_cloud:
                logger.info("Step 7: Saving to cloud...")
                cloud_url = self.cloud.upload_file(
                    final_video, 
                    options.cloud_provider
                )
                logger.info(f"Video uploaded to cloud: {cloud_url}")
            
            # Update statistics
            self._update_statistics(chunks, timer.elapsed())
            
            # Cleanup
            self._cleanup_temp_files()
            
            result = {
                'success': True,
                'output_path': final_video,
                'duration': sum(c['total_duration'] for c in chunks),
                'generation_time': timer.elapsed(),
                'chunks_processed': len(chunks),
                'message': 'Video generated successfully'
            }
            
            logger.info(f"Video generation completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'output_path': None,
                'message': f'Video generation failed: {e}'
            }
    
    def _generate_audio_for_chunks(self, chunks: List[Dict], 
                                 options: GenerationOptions) -> List[str]:
        """Generate audio files for each chunk"""
        audio_files = []
        
        for i, chunk in enumerate(chunks):
            chunk_text = " ".join([s['text'] for s in chunk['scenes']])
            audio_file = f"{self.config['project']['temp_dir']}/audio_chunk_{i}.mp3"
            
            success = self.tts.generate_speech(
                text=chunk_text,
                output_file=audio_file,
                engine=options.voice_engine,
                language=self.config['text_to_speech']['language'],
                rate=self.config['text_to_speech']['rate']
            )
            
            if success:
                audio_files.append(audio_file)
            else:
                logger.warning(f"Audio generation failed for chunk {i}")
                # Use placeholder or skip
            
        return audio_files
    
    def _generate_images_for_chunks(self, chunks: List[Dict],
                                  options: GenerationOptions) -> List[List[str]]:
        """Generate images for each scene in chunks"""
        all_images = []
        
        for chunk_idx, chunk in enumerate(chunks):
            chunk_images = []
            for scene_idx, scene in enumerate(chunk['scenes']):
                prompt = scene.get('image_prompt', scene['text'][:100])
                image_file = (f"{self.config['project']['temp_dir']}/"
                            f"image_{chunk_idx}_{scene_idx}.jpg")
                
                success = self.images.generate_image(
                    prompt=prompt,
                    output_file=image_file,
                    engine=options.image_engine,
                    size=self._get_image_size(options.quality)
                )
                
                if success:
                    chunk_images.append(image_file)
                else:
                    # Create placeholder
                    placeholder = self._create_placeholder_image(
                        prompt, image_file
                    )
                    chunk_images.append(placeholder)
            
            all_images.append(chunk_images)
        
        return all_images
    
    def _create_video_chunks(self, chunks: List[Dict],
                           audio_files: List[str],
                           image_files: List[List[str]],
                           options: GenerationOptions) -> List[str]:
        """Create video chunks from audio and images"""
        video_chunks = []
        
        for i, (chunk, audio_file, images) in enumerate(
            zip(chunks, audio_files, image_files)):
            
            output_file = (f"{self.config['project']['temp_dir']}/"
                         f"video_chunk_{i}.mp4")
            
            # Calculate durations
            durations = [s['duration'] for s in chunk['scenes']]
            
            success = self.video.create_slideshow(
                images=images,
                audio_file=audio_file,
                output_file=output_file,
                durations=durations,
                resolution=self._get_resolution(options.quality),
                fps=self.config['video']['fps']
            )
            
            if success:
                video_chunks.append(output_file)
            else:
                logger.warning(f"Video chunk creation failed for chunk {i}")
        
        return video_chunks
    
    def _merge_video_chunks(self, video_chunks: List[str], 
                          output_path: str) -> bool:
        """Merge video chunks into final video"""
        if len(video_chunks) == 1:
            # Just copy the single chunk
            import shutil
            shutil.copy(video_chunks[0], output_path)
            return True
        
        return self.video.merge_videos(video_chunks, output_path)
    
    def _enhance_video(self, video_path: str, chunks: List[Dict],
                      options: GenerationOptions) -> str:
        """Add enhancements to video"""
        enhanced_path = video_path
        
        # Add subtitles
        if options.add_subtitles:
            subtitles = self._generate_subtitles(chunks)
            subtitle_path = video_path.replace('.mp4', '_subtitled.mp4')
            if self.video.add_subtitles(video_path, subtitles, subtitle_path):
                enhanced_path = subtitle_path
        
        # Add transitions
        if options.add_transitions:
            transition_path = enhanced_path.replace('.mp4', '_transitions.mp4')
            if self.video.add_transitions(enhanced_path, transition_path):
                if enhanced_path != video_path:
                    # Remove intermediate file
                    import os
                    os.remove(enhanced_path)
                enhanced_path = transition_path
        
        # Add background music
        if options.add_background_music and options.background_music_path:
            music_path = enhanced_path.replace('.mp4', '_music.mp4')
            if self.video.add_background_music(
                enhanced_path, 
                options.background_music_path,
                music_path
            ):
                if enhanced_path != video_path:
                    import os
                    os.remove(enhanced_path)
                enhanced_path = music_path
        
        return enhanced_path
    
    def _generate_subtitles(self, chunks: List[Dict]) -> List[Dict]:
        """Generate subtitle timings"""
        subtitles = []
        current_time = 0
        
        for chunk in chunks:
            for scene in chunk['scenes']:
                # Split long text into multiple subtitles
                text_chunks = self._split_text_for_subtitles(scene['text'])
                chunk_duration = scene['duration'] / len(text_chunks)
                
                for text_chunk in text_chunks:
                    subtitles.append({
                        'text': text_chunk,
                        'start': current_time,
                        'end': current_time + chunk_duration
                    })
                    current_time += chunk_duration
        
        return subtitles
    
    def _split_text_for_subtitles(self, text: str, max_chars: int = 40) -> List[str]:
        """Split text for subtitle display"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _get_resolution(self, quality: VideoQuality) -> str:
        """Get resolution based on quality"""
        resolutions = {
            VideoQuality.LOW: "1280x720",
            VideoQuality.MEDIUM: "1920x1080",
            VideoQuality.HIGH: "2560x1440",
            VideoQuality.ULTRA: "3840x2160"
        }
        return resolutions.get(quality, "1920x1080")
    
    def _get_image_size(self, quality: VideoQuality) -> tuple:
        """Get image size based on quality"""
        sizes = {
            VideoQuality.LOW: (768, 432),
            VideoQuality.MEDIUM: (1024, 576),
            VideoQuality.HIGH: (1536, 864),
            VideoQuality.ULTRA: (2048, 1152)
        }
        return sizes.get(quality, (1024, 576))
    
    def _create_placeholder_image(self, prompt: str, output_file: str) -> str:
        """Create placeholder image"""
        from PIL import Image, ImageDraw, ImageFont
        import os
        
        img = Image.new('RGB', (1024, 576), color=(53, 73, 94))
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use system font
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 36)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Add text
        draw.text((50, 250), prompt[:50], fill=(255, 255, 255), font=font)
        draw.text((50, 300), "AI Generated Image", fill=(200, 200, 200), font=font)
        
        img.save(output_file)
        return output_file
    
    def _update_statistics(self, chunks: List[Dict], generation_time: float):
        """Update generation statistics"""
        duration = sum(c['total_duration'] for c in chunks)
        
        self.stats['total_videos'] += 1
        self.stats['total_duration'] += duration
        
        # Update average generation time
        total_time = (self.stats['average_generation_time'] * 
                     (self.stats['total_videos'] - 1) + generation_time)
        self.stats['average_generation_time'] = total_time / self.stats['total_videos']
        
        # Update success rate (simplified)
        self.stats['success_rate'] = 0.95  # Placeholder
    
    def _cleanup_temp_files(self):
        """Cleanup temporary files"""
        import shutil
        import os
        
        temp_dir = self.config['project']['temp_dir']
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            logger.debug("Temporary files cleaned up")
    
    def batch_generate(self, scripts: Dict[str, str], 
                      output_dir: str,
                      options: Optional[GenerationOptions] = None) -> Dict[str, Dict]:
        """Batch generate multiple videos
        
        Args:
            scripts: Dictionary of script names to script text
            output_dir: Directory to save output videos
            options: Generation options
            
        Returns:
            Dictionary of results for each script
        """
        results = {}
        
        for name, script_text in scripts.items():
            output_path = os.path.join(output_dir, f"{name}.mp4")
            logger.info(f"Processing script: {name}")
            
            result = self.generate_from_script(
                script_text, output_path, options
            )
            
            results[name] = result
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return self.stats.copy()
    
    def reset_statistics(self):
        """Reset statistics"""
        self.stats = {
            'total_videos': 0,
            'total_duration': 0,
            'success_rate': 0.0,
            'average_generation_time': 0.0
        }
        logger.info("Statistics reset")

# Factory function for easy creation
def create_video_generator(config_path: Optional[str] = None) -> AdvancedVideoGenerator:
    """Create and configure a video generator
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configured AdvancedVideoGenerator instance
    """
    return AdvancedVideoGenerator(config_path)

# Export main class
__all__ = ['AdvancedVideoGenerator', 'GenerationOptions', 'VideoQuality', 
           'create_video_generator']
