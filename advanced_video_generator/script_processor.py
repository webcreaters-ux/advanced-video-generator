"""
Script processing module for video generator
"""

import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Scene:
    """Represents a single scene in the script"""
    text: str
    duration: float
    image_prompt: Optional[str] = None
    transition: Optional[str] = None


class ScriptProcessor:
    """Process scripts into video scenes"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize script processor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.text_config = config.get('text', {})
        self.words_per_minute = self.text_config.get('words_per_minute', 150)
        self.max_scene_duration = self.text_config.get('max_scene_duration', 30)
        self.min_scene_duration = self.text_config.get('min_scene_duration', 3)
    
    def parse_script(self,
                    script_text: str,
                    max_chunk_duration: int = 300) -> List[Dict]:
        """Parse script text into chunks and scenes
        
        Args:
            script_text: The script text to parse
            max_chunk_duration: Maximum duration per chunk in seconds
            
        Returns:
            List of chunk dictionaries with scenes
        """
        # Clean script
        script_text = self._clean_script(script_text)
        
        # Split into paragraphs/lines
        paragraphs = self._split_paragraphs(script_text)
        
        # Create scenes
        scenes = self._create_scenes(paragraphs)
        
        # Group into chunks
        chunks = self._create_chunks(scenes, max_chunk_duration)
        
        logger.info(f"Parsed script into {len(chunks)} chunks with {sum(len(c['scenes']) for c in chunks)} scenes")
        
        return chunks
    
    def _clean_script(self, text: str) -> str:
        """Clean script text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:\'"-]', '', text)
        
        return text.strip()
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newlines or single newlines
        paragraphs = re.split(r'\n\s*\n|\n', text)
        
        # Filter empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _create_scenes(self, paragraphs: List[str]) -> List[Scene]:
        """Create scenes from paragraphs"""
        scenes = []
        
        for para in paragraphs:
            # Calculate duration based on word count
            word_count = len(para.split())
            duration = (word_count / self.words_per_minute) * 60
            
            # Clamp duration
            duration = max(self.min_scene_duration, min(duration, self.max_scene_duration))
            
            # Create scene
            scene = Scene(
                text=para,
                duration=duration,
                image_prompt=self._generate_image_prompt(para)
            )
            scenes.append(scene)
        
        return scenes
    
    def _generate_image_prompt(self, text: str) -> str:
        """Generate an image prompt from text"""
        # Extract key words for image generation
        words = text.split()
        
        # Take first few meaningful words
        meaningful_words = []
        skip_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                     'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                     'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                     'through', 'during', 'before', 'after', 'above', 'below',
                     'between', 'under', 'again', 'further', 'then', 'once'}
        
        for word in words:
            if word.lower() not in skip_words:
                meaningful_words.append(word)
            if len(meaningful_words) >= 10:
                break
        
        prompt = ' '.join(meaningful_words)
        return prompt if prompt else text[:50]
    
    def _create_chunks(self, scenes: List[Scene], max_duration: int) -> List[Dict]:
        """Group scenes into chunks"""
        chunks = []
        current_chunk = {'scenes': [], 'total_duration': 0}
        
        for scene in scenes:
            # Check if adding this scene would exceed max duration
            if current_chunk['total_duration'] + scene.duration > max_duration:
                if current_chunk['scenes']:
                    chunks.append(current_chunk)
                current_chunk = {'scenes': [], 'total_duration': 0}
            
            current_chunk['scenes'].append({
                'text': scene.text,
                'duration': scene.duration,
                'image_prompt': scene.image_prompt
            })
            current_chunk['total_duration'] += scene.duration
        
        # Add final chunk
        if current_chunk['scenes']:
            chunks.append(current_chunk)
        
        return chunks
    
    def enhance_with_ai(self, text: str) -> str:
        """Enhance script text using AI (placeholder)"""
        # This would integrate with an AI model for script enhancement
        # For now, just return the original text
        return text
    
    def estimate_total_duration(self, script_text: str) -> float:
        """Estimate total duration of the script
        
        Args:
            script_text: The script text
            
        Returns:
            Estimated duration in seconds
        """
        word_count = len(script_text.split())
        return (word_count / self.words_per_minute) * 60
    
    def get_word_count(self, script_text: str) -> int:
        """Get word count of script
        
        Args:
            script_text: The script text
            
        Returns:
            Word count
        """
        return len(script_text.split())
    
    def get_statistics(self, script_text: str) -> Dict[str, Any]:
        """Get statistics about the script
        
        Args:
            script_text: The script text
            
        Returns:
            Dictionary with statistics
        """
        chunks = self.parse_script(script_text)
        
        return {
            'word_count': self.get_word_count(script_text),
            'estimated_duration': self.estimate_total_duration(script_text),
            'num_chunks': len(chunks),
            'num_scenes': sum(len(c['scenes']) for c in chunks),
            'avg_scene_duration': sum(
                s['duration'] for c in chunks for s in c['scenes']
            ) / sum(len(c['scenes']) for c in chunks) if chunks else 0
        }


__all__ = ['ScriptProcessor', 'Scene']
