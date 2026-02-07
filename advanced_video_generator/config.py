"""
Configuration management for video generator
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manage configuration for video generation"""
    
    DEFAULT_CONFIG = {
        "project": {
            "name": "video_generator",
            "output_dir": "./output",
            "temp_dir": "./temp",
            "log_dir": "./logs",
            "cache_dir": "./cache",
            "models_dir": "./models"
        },
        "video": {
            "default_resolution": "1920x1080",
            "default_fps": 30,
            "default_codec": "libx264",
            "default_crf": 23,
            "default_preset": "medium",
            "audio_bitrate": "192k",
            "supported_resolutions": [
                "1280x720",
                "1920x1080", 
                "2560x1440",
                "3840x2160",
                "1080x1920",
                "720x1280"
            ],
            "supported_formats": ["mp4", "avi", "mov", "mkv"]
        },
        "audio": {
            "tts_engine": "google",
            "default_language": "en-US",
            "default_rate": 1.0,
            "default_volume": 1.0,
            "cache_tts": True,
            "fallback_engines": ["google", "edge", "pyttsx3"],
            "background_music": {
                "enabled": False,
                "volume": 0.3,
                "fade_duration": 2.0
            }
        },
        "images": {
            "generation_engine": "stable_diffusion",
            "default_model": "stabilityai/stable-diffusion-2-1",
            "default_size": [1024, 768],
            "num_inference_steps": 25,
            "guidance_scale": 7.5,
            "negative_prompt": "blurry, ugly, deformed, text, watermark",
            "cache_images": True,
            "use_stock_images": True,
            "stock_sources": ["pexels", "pixabay", "unsplash"],
            "api_keys": {
                "pexels": "",
                "pixabay": "",
                "unsplash": ""
            }
        },
        "text": {
            "chunk_duration": 300,
            "max_scene_duration": 30,
            "min_scene_duration": 3,
            "words_per_minute": 150,
            "enhance_with_ai": False,
            "ai_model": "gpt2"
        },
        "processing": {
            "parallel_processing": True,
            "max_workers": 4,
            "gpu_acceleration": True,
            "memory_limit": 4096,  # MB
            "cleanup_temp": True,
            "save_intermediate": False
        },
        "cloud": {
            "save_to_cloud": False,
            "providers": ["google_drive", "dropbox", "aws_s3"],
            "google_drive": {
                "enabled": False,
                "folder": "VideoGenerator"
            },
            "dropbox": {
                "enabled": False,
                "access_token": ""
            },
            "aws_s3": {
                "enabled": False,
                "bucket": "",
                "region": "us-east-1"
            }
        },
        "extensions": {
            "voice_cloning": False,
            "advanced_transitions": False,
            "auto_captions": False,
            "social_media_formats": False,
            "video_analytics": False
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file_format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            "max_file_size": 10485760,  # 10MB
            "backup_count": 5
        }
    }
    
    @classmethod
    def load_config(cls, config_path: Optional[str] = None, 
                   create_default: bool = True) -> Dict[str, Any]:
        """Load configuration from file or use defaults
        
        Args:
            config_path: Path to configuration file
            create_default: Create default config if file doesn't exist
            
        Returns:
            Configuration dictionary
        """
        config = cls.DEFAULT_CONFIG.copy()
        
        # Try to load from file
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                        file_config = yaml.safe_load(f)
                    elif config_path.endswith('.json'):
                        file_config = json.load(f)
                    else:
                        # Try both formats
                        try:
                            f.seek(0)
                            file_config = yaml.safe_load(f)
                        except:
                            f.seek(0)
                            file_config = json.load(f)
                
                # Deep merge configurations
                config = cls._deep_merge(config, file_config)
                logger.info(f"Loaded configuration from {config_path}")
                
            except Exception as e:
                logger.error(f"Failed to load config from {config_path}: {e}")
                if create_default:
                    cls._save_default_config(config_path, config)
        
        elif config_path and create_default:
            # Create default config file
            cls._save_default_config(config_path, config)
            logger.info(f"Created default configuration at {config_path}")
        
        # Set environment variables
        cls._set_env_variables(config)
        
        return config
    
    @classmethod
    def _deep_merge(cls, base: Dict, update: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @classmethod
    def _save_default_config(cls, config_path: str, config: Dict):
        """Save default configuration to file"""
        try:
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)
            
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
            else:
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save default config: {e}")
    
    @classmethod
    def _set_env_variables(cls, config: Dict):
        """Set environment variables from config"""
        # Set Hugging Face cache dir if not set
        if 'HF_HOME' not in os.environ:
            cache_dir = config['project'].get('cache_dir', './cache')
            os.environ['HF_HOME'] = os.path.abspath(cache_dir)
        
        # Set torch home
        if 'TORCH_HOME' not in os.environ:
            models_dir = config['project'].get('models_dir', './models')
            os.environ['TORCH_HOME'] = os.path.abspath(models_dir)
        
        # Set API keys
        api_keys = config['images'].get('api_keys', {})
        for service, key in api_keys.items():
            if key:
                env_var = f"{service.upper()}_API_KEY"
                if env_var not in os.environ:
                    os.environ[env_var] = key
    
    @classmethod
    def save_config(cls, config: Dict, config_path: str):
        """Save configuration to file
        
        Args:
            config: Configuration dictionary
            config_path: Path to save configuration
        """
        try:
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)
            
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
            else:
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    @classmethod
    def validate_config(cls, config: Dict) -> tuple[bool, list]:
        """Validate configuration
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required directories
        project_config = config.get('project', {})
        required_dirs = ['output_dir', 'temp_dir', 'log_dir']
        
        for dir_key in required_dirs:
            if dir_key not in project_config:
                errors.append(f"Missing project.{dir_key}")
            elif not project_config[dir_key]:
                errors.append(f"Empty project.{dir_key}")
        
        # Check video settings
        video_config = config.get('video', {})
        if 'default_resolution' not in video_config:
            errors.append("Missing video.default_resolution")
        else:
            resolution = video_config['default_resolution']
            if 'x' not in resolution:
                errors.append(f"Invalid resolution format: {resolution}")
            else:
                try:
                    width, height = map(int, resolution.split('x'))
                    if width <= 0 or height <= 0:
                        errors.append(f"Invalid resolution dimensions: {resolution}")
                except ValueError:
                    errors.append(f"Invalid resolution format: {resolution}")
        
        # Check TTS settings
        audio_config = config.get('audio', {})
        if 'tts_engine' not in audio_config:
            errors.append("Missing audio.tts_engine")
        else:
            valid_engines = ['google', 'edge', 'coqui', 'pyttsx3']
            if audio_config['tts_engine'] not in valid_engines:
                errors.append(f"Invalid TTS engine: {audio_config['tts_engine']}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def create_config_template(cls, output_path: str = "config_template.yaml"):
        """Create a configuration template file
        
        Args:
            output_path: Path to save template
        """
        template = cls.DEFAULT_CONFIG.copy()
        
        # Add comments/descriptions
        template_with_comments = {
            "# Advanced Video Generator Configuration": None,
            "# Generated on": None,
            "#": None,
            "project": {
                "# Project settings": None,
                "name": "video_generator",
                "output_dir": "./output",
                "temp_dir": "./temp",
                "log_dir": "./logs",
                "cache_dir": "./cache",
                "models_dir": "./models"
            },
            "video": {
                "# Video settings": None,
                "default_resolution": "1920x1080",
                "default_fps": 30,
                "default_codec": "libx264",
                "default_crf": 23,
                "default_preset": "medium",
                "audio_bitrate": "192k"
            },
            "audio": {
                "# Audio settings": None,
                "tts_engine": "google",
                "default_language": "en-US",
                "default_rate": 1.0,
                "default_volume": 1.0,
                "cache_tts": True
            },
            "images": {
                "# Image generation settings": None,
                "generation_engine": "stable_diffusion",
                "default_model": "stabilityai/stable-diffusion-2-1",
                "default_size": [1024, 768],
                "num_inference_steps": 25,
                "guidance_scale": 7.5
            }
        }
        
        # Save as YAML
        with open(output_path, 'w') as f:
            f.write("# Advanced Video Generator Configuration\n")
            f.write("# Edit this file to customize settings\n\n")
            
            import yaml
            yaml.dump(template, f, default_flow_style=False)
        
        logger.info(f"Configuration template saved to {output_path}")
        return output_path
    
    @classmethod
    def get_config_value(cls, config: Dict, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation
        
        Args:
            config: Configuration dictionary
            key_path: Dot notation path (e.g., "video.default_resolution")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    @classmethod
    def set_config_value(cls, config: Dict, key_path: str, value: Any):
        """Set configuration value using dot notation
        
        Args:
            config: Configuration dictionary
            key_path: Dot notation path
            value: Value to set
        """
        keys = key_path.split('.')
        current = config
        
        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value

# Utility function for easy config loading
def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or use defaults
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    return ConfigManager.load_config(config_path)

__all__ = ['ConfigManager', 'load_config']
