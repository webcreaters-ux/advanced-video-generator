"""
Text-to-Speech Generator Module
Multiple TTS engines with fallback support
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TTSConfig:
    """TTS Configuration"""
    engine: str = "google"
    language: str = "en-US"
    rate: float = 1.0
    volume: float = 1.0
    voice: Optional[str] = None
    cache_dir: str = "./tts_cache"
    fallback_engines: list = None

class TTSBase(ABC):
    """Base class for TTS engines"""
    
    def __init__(self, config: TTSConfig):
        self.config = config
        self.cache_dir = Path(config.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    @abstractmethod
    def generate(self, text: str, output_file: str) -> bool:
        """Generate speech from text"""
        pass
    
    def get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        key_data = f"{text}_{self.config.engine}_{self.config.language}_{self.config.rate}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_file(self, text: str) -> Optional[str]:
        """Get cached file if exists"""
        cache_key = self.get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        return str(cache_file) if cache_file.exists() else None

class GoogleTTS(TTSBase):
    """Google Text-to-Speech"""
    
    def generate(self, text: str, output_file: str) -> bool:
        try:
            from gtts import gTTS
            
            # Split long text
            chunks = self._split_text(text)
            if len(chunks) > 1:
                return self._generate_chunked(chunks, output_file)
            
            tts = gTTS(
                text=text,
                lang=self.config.language[:2],
                slow=False
            )
            tts.save(output_file)
            return True
            
        except Exception as e:
            logger.error(f"Google TTS failed: {e}")
            return False
    
    def _split_text(self, text: str, max_chars: int = 200) -> list:
        """Split text for TTS limits"""
        import re
        
        # Split by sentences if possible
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            sentence = sentence.strip() + "."
            
            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [text[:max_chars]]
    
    def _generate_chunked(self, chunks: list, output_file: str) -> bool:
        """Generate speech in chunks and merge"""
        try:
            from pydub import AudioSegment
            import tempfile
            
            audio_segments = []
            
            for i, chunk in enumerate(chunks):
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                    tmp_path = tmp.name
                    
                    tts = gTTS(
                        text=chunk,
                        lang=self.config.language[:2],
                        slow=False
                    )
                    tts.save(tmp_path)
                    
                    audio = AudioSegment.from_mp3(tmp_path)
                    audio_segments.append(audio)
                    
                    os.unlink(tmp_path)
            
            # Combine all segments
            combined = AudioSegment.empty()
            for segment in audio_segments:
                combined += segment
            
            combined.export(output_file, format="mp3")
            return True
            
        except Exception as e:
            logger.error(f"Chunked TTS failed: {e}")
            return False

class EdgeTTS(TTSBase):
    """Microsoft Edge TTS"""
    
    def generate(self, text: str, output_file: str) -> bool:
        try:
            import edge_tts
            import asyncio
            
            voice = self._get_voice()
            
            async def _generate():
                tts = edge_tts.Communicate(
                    text=text,
                    voice=voice,
                    rate=self._get_rate_string()
                )
                await tts.save(output_file)
            
            asyncio.run(_generate())
            return True
            
        except Exception as e:
            logger.error(f"Edge TTS failed: {e}")
            return False
    
    def _get_voice(self) -> str:
        """Get voice for language"""
        voices = {
            "en-US": "en-US-AriaNeural",
            "en-GB": "en-GB-SoniaNeural",
            "es-ES": "es-ES-ElviraNeural",
            "fr-FR": "fr-FR-DeniseNeural",
            "de-DE": "de-DE-KatjaNeural",
            "it-IT": "it-IT-ElsaNeural",
            "ja-JP": "ja-JP-NanamiNeural",
            "ko-KR": "ko-KR-SunHiNeural",
            "zh-CN": "zh-CN-XiaoxiaoNeural",
        }
        return voices.get(self.config.language, "en-US-AriaNeural")
    
    def _get_rate_string(self) -> str:
        """Convert rate to Edge TTS format"""
        if self.config.rate > 1:
            return f"+{int((self.config.rate - 1) * 100)}%"
        elif self.config.rate < 1:
            return f"{int((1 - self.config.rate) * 100)}%"
        return "+0%"

class CoquiTTS(TTSBase):
    """Coqui TTS (offline)"""
    
    def __init__(self, config: TTSConfig):
        super().__init__(config)
        self.model = None
    
    def generate(self, text: str, output_file: str) -> bool:
        try:
            if self.model is None:
                self._load_model()
            
            self.model.tts_to_file(
                text=text,
                file_path=output_file,
                speaker=self.config.voice
            )
            return True
            
        except Exception as e:
            logger.error(f"Coqui TTS failed: {e}")
            return False
    
    def _load_model(self):
        """Load TTS model"""
        try:
            from TTS.api import TTS
            
            # Select model based on language
            models = {
                "en": "tts_models/en/ljspeech/tacotron2-DDC",
                "es": "tts_models/es/css10/vits",
                "fr": "tts_models/fr/css10/vits",
                "de": "tts_models/de/css10/vits",
                "it": "tts_models/it/css10/vits",
            }
            
            lang_code = self.config.language[:2]
            model_name = models.get(lang_code, "tts_models/en/ljspeech/tacotron2-DDC")
            
            self.model = TTS(model_name=model_name)
            logger.info(f"Loaded Coqui TTS model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load Coqui TTS model: {e}")
            raise

class Pyttsx3TTS(TTSBase):
    """pyttsx3 TTS (offline, system voices)"""
    
    def __init__(self, config: TTSConfig):
        super().__init__(config)
        self.engine = None
    
    def generate(self, text: str, output_file: str) -> bool:
        try:
            if self.engine is None:
                self._init_engine()
            
            self.engine.save_to_file(text, output_file)
            self.engine.runAndWait()
            return True
            
        except Exception as e:
            logger.error(f"pyttsx3 TTS failed: {e}")
            return False
    
    def _init_engine(self):
        """Initialize pyttsx3 engine"""
        import pyttsx3
        
        self.engine = pyttsx3.init()
        
        # Set properties
        self.engine.setProperty('rate', 150 * self.config.rate)
        self.engine.setProperty('volume', self.config.volume)
        
        # Set voice if specified
        if self.config.voice:
            self.engine.setProperty('voice', self.config.voice)
        else:
            # Try to find voice for language
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if self.config.language[:2].lower() in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break

class TTSGenerator:
    """Main TTS generator with multiple engines and fallback"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        tts_config = TTSConfig(
            engine=config.get('tts_engine', 'google'),
            language=config.get('language', 'en-US'),
            rate=config.get('rate', 1.0),
            volume=config.get('volume', 1.0),
            cache_dir=config.get('cache_dir', './tts_cache'),
            fallback_engines=config.get('fallback_engines', 
                                       ['google', 'edge', 'pyttsx3'])
        )
        
        self.engines = {
            'google': GoogleTTS(tts_config),
            'edge': EdgeTTS(tts_config),
            'coqui': CoquiTTS(tts_config),
            'pyttsx3': Pyttsx3TTS(tts_config)
        }
    
    def generate_speech(self, text: str, output_file: str, 
                       engine: Optional[str] = None, 
                       use_cache: bool = True) -> bool:
        """Generate speech with caching and fallback
        
        Args:
            text: Text to convert to speech
            output_file: Output file path
            engine: Preferred TTS engine
            use_cache: Use cached files if available
            
        Returns:
            True if successful, False otherwise
        """
        if not text.strip():
            logger.warning("Empty text provided for TTS")
            return False
        
        engine = engine or self.config.get('tts_engine', 'google')
        
        # Check cache first
        if use_cache:
            cached = self._get_cached(text, engine)
            if cached and os.path.exists(cached):
                import shutil
                shutil.copy(cached, output_file)
                logger.debug(f"Using cached TTS for: {text[:50]}...")
                return True
        
        # Try preferred engine
        if engine in self.engines:
            if self.engines[engine].generate(text, output_file):
                self._cache_result(text, engine, output_file)
                return True
        
        # Try fallback engines
        fallbacks = self.config.get('fallback_engines', 
                                   ['google', 'edge', 'pyttsx3'])
        
        for fallback in fallbacks:
            if fallback != engine and fallback in self.engines:
                logger.info(f"Trying fallback engine: {fallback}")
                if self.engines[fallback].generate(text, output_file):
                    self._cache_result(text, fallback, output_file)
                    return True
        
        logger.error("All TTS engines failed")
        return False
    
    def _get_cached(self, text: str, engine: str) -> Optional[str]:
        """Get cached file path"""
        tts_engine = self.engines.get(engine)
        if tts_engine:
            return tts_engine.get_cached_file(text)
        return None
    
    def _cache_result(self, text: str, engine: str, output_file: str):
        """Cache the generated result"""
        tts_engine = self.engines.get(engine)
        if tts_engine:
            cache_key = tts_engine.get_cache_key(text)
            cache_file = tts_engine.cache_dir / f"{cache_key}.mp3"
            
            import shutil
            shutil.copy(output_file, str(cache_file))
            logger.debug(f"Cached TTS result: {cache_key}")
    
    def list_voices(self, engine: str = None) -> Dict[str, list]:
        """List available voices for engines"""
        voices = {}
        
        if engine:
            engines_to_check = [engine]
        else:
            engines_to_check = list(self.engines.keys())
        
        for eng in engines_to_check:
            if eng == 'pyttsx3':
                try:
                    import pyttsx3
                    pyttsx3_engine = pyttsx3.init()
                    pyttsx3_voices = [v.id for v in pyttsx3_engine.getProperty('voices')]
                    voices['pyttsx3'] = pyttsx3_voices
                    pyttsx3_engine.stop()
                except:
                    voices['pyttsx3'] = []
            
            elif eng == 'edge':
                # Edge TTS voices
                edge_voices = [
                    "en-US-AriaNeural",
                    "en-US-GuyNeural",
                    "en-GB-SoniaNeural",
                    "es-ES-ElviraNeural",
                    "fr-FR-DeniseNeural"
                ]
                voices['edge'] = edge_voices
        
        return voices
    
    def get_engine_info(self) -> Dict[str, Dict]:
        """Get information about available engines"""
        info = {}
        
        for name, engine in self.engines.items():
            info[name] = {
                'online': name in ['google', 'edge'],
                'languages': self._get_supported_languages(name),
                'quality': self._get_quality_rating(name),
                'speed': self._get_speed_rating(name)
            }
        
        return info
    
    def _get_supported_languages(self, engine: str) -> list:
        """Get supported languages for engine"""
        languages = {
            'google': ['en', 'es', 'fr', 'de', 'it', 'ja', 'ko', 'zh'],
            'edge': ['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE', 'it-IT', 'ja-JP', 'ko-KR', 'zh-CN'],
            'coqui': ['en', 'es', 'fr', 'de', 'it'],
            'pyttsx3': ['en', 'es', 'fr', 'de', 'it']  # System dependent
        }
        return languages.get(engine, [])
    
    def _get_quality_rating(self, engine: str) -> str:
        """Get quality rating"""
        ratings = {
            'google': 'high',
            'edge': 'very high',
            'coqui': 'medium',
            'pyttsx3': 'low'
        }
        return ratings.get(engine, 'unknown')
    
    def _get_speed_rating(self, engine: str) -> str:
        """Get speed rating"""
        ratings = {
            'google': 'fast',
            'edge': 'medium',
            'coqui': 'slow',
            'pyttsx3': 'fast'
        }
        return ratings.get(engine, 'unknown')
