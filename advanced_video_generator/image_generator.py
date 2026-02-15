"""
Image generation module for video generator
"""

import os
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generate images for video scenes using AI"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize image generator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.image_config = config.get('image_generation', {})
        self.model = self.image_config.get('model', 'stabilityai/stable-diffusion-2-1')
        self.steps = self.image_config.get('steps', 25)
        self.guidance_scale = self.image_config.get('guidance_scale', 7.5)
        self.negative_prompt = self.image_config.get(
            'negative_prompt', 
            'blurry, ugly, deformed, text, watermark'
        )
        self._pipeline = None
    
    def _load_pipeline(self):
        """Load the image generation pipeline"""
        if self._pipeline is not None:
            return
        
        try:
            import torch
            from diffusers import StableDiffusionPipeline
            
            logger.info(f"Loading image model: {self.model}")
            
            # Check for GPU
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self._pipeline = StableDiffusionPipeline.from_pretrained(
                self.model,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            )
            self._pipeline = self._pipeline.to(device)
            
            # Enable memory efficient attention if available
            if hasattr(self._pipeline, 'enable_attention_slicing'):
                self._pipeline.enable_attention_slicing()
            
            logger.info(f"Image model loaded on {device}")
            
        except ImportError as e:
            logger.warning(f"Could not load image model: {e}")
            logger.warning("Image generation will use placeholders")
    
    def generate_image(self,
                       prompt: str,
                       output_file: str,
                       engine: str = "stable_diffusion",
                       size: Tuple[int, int] = (1024, 576),
                       num_attempts: int = 3) -> bool:
        """Generate an image from a prompt
        
        Args:
            prompt: Text description for image generation
            output_file: Path to save the image
            engine: Image generation engine
            size: Image size (width, height)
            num_attempts: Number of attempts on failure
            
        Returns:
            True if successful
        """
        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        if engine == "stable_diffusion":
            return self._generate_stable_diffusion(prompt, output_file, size, num_attempts)
        elif engine == "placeholder":
            return self._generate_placeholder(prompt, output_file, size)
        else:
            logger.warning(f"Unknown engine: {engine}, using placeholder")
            return self._generate_placeholder(prompt, output_file, size)
    
    def _generate_stable_diffusion(self,
                                   prompt: str,
                                   output_file: str,
                                   size: Tuple[int, int],
                                   num_attempts: int) -> bool:
        """Generate image using Stable Diffusion"""
        try:
            self._load_pipeline()
            
            if self._pipeline is None:
                return self._generate_placeholder(prompt, output_file, size)
            
            import torch
            
            # Enhance prompt
            enhanced_prompt = f"{prompt}, high quality, detailed, professional"
            
            for attempt in range(num_attempts):
                try:
                    # Generate image
                    image = self._pipeline(
                        prompt=enhanced_prompt,
                        negative_prompt=self.negative_prompt,
                        num_inference_steps=self.steps,
                        guidance_scale=self.guidance_scale,
                        width=size[0],
                        height=size[1]
                    ).images[0]
                    
                    # Save image
                    image.save(output_file)
                    logger.info(f"Generated image: {output_file}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"Image generation attempt {attempt + 1} failed: {e}")
                    if attempt == num_attempts - 1:
                        raise
            
        except Exception as e:
            logger.error(f"Stable Diffusion generation failed: {e}")
            return self._generate_placeholder(prompt, output_file, size)
        
        return False
    
    def _generate_placeholder(self,
                             prompt: str,
                             output_file: str,
                             size: Tuple[int, int]) -> bool:
        """Generate a placeholder image"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create image with gradient background
            img = Image.new('RGB', size, color=(53, 73, 94))
            draw = ImageDraw.Draw(img)
            
            # Add gradient effect
            for i in range(size[1]):
                alpha = int(255 * (1 - i / size[1]))
                draw.line([(0, i), (size[0], i)], 
                         fill=(53 + alpha // 8, 73 + alpha // 8, 94 + alpha // 8))
            
            # Try to load font
            try:
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 24)
                    small_font = ImageFont.truetype(font_path, 16)
                else:
                    font = ImageFont.load_default()
                    small_font = font
            except Exception:
                font = ImageFont.load_default()
                small_font = font
            
            # Add text
            text = prompt[:60] + "..." if len(prompt) > 60 else prompt
            draw.text((30, size[1] // 2 - 30), text, fill=(255, 255, 255), font=font)
            draw.text((30, size[1] // 2 + 20), "AI Generated Placeholder", 
                     fill=(200, 200, 200), font=small_font)
            
            # Save image
            img.save(output_file)
            logger.info(f"Generated placeholder: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Placeholder generation failed: {e}")
            return False
    
    def batch_generate(self,
                       prompts: list,
                       output_dir: str,
                       **kwargs) -> list:
        """Generate multiple images
        
        Args:
            prompts: List of prompts
            output_dir: Directory to save images
            **kwargs: Additional arguments for generate_image
            
        Returns:
            List of output file paths
        """
        output_files = []
        
        for i, prompt in enumerate(prompts):
            output_file = os.path.join(output_dir, f"image_{i:04d}.jpg")
            success = self.generate_image(prompt, output_file, **kwargs)
            if success:
                output_files.append(output_file)
        
        return output_files


__all__ = ['ImageGenerator']
