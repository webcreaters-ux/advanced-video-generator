"""
Video Analytics Extension
Analyze video performance and engagement
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoAnalytics:
    """Analyze video performance and engagement"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize video analytics
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    def analyze_video(self, video_file: str) -> Dict[str, Any]:
        """Analyze a video file
        
        Args:
            video_file: Path to video file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            from moviepy.editor import VideoFileClip
            
            # Load video
            video = VideoFileClip(video_file)
            
            # Basic analysis
            analysis = {
                'file': video_file,
                'duration': video.duration,
                'fps': video.fps,
                'size': video.size,
                'aspect_ratio': video.size[0] / video.size[1],
                'has_audio': video.audio is not None if video else False
            }
            
            # Additional analysis
            if video.audio:
                analysis['audio_duration'] = video.audio.duration
                analysis['audio_fps'] = video.audio.fps
            
            video.close()
            
            # Get file size
            if os.path.exists(video_file):
                analysis['file_size_mb'] = os.path.getsize(video_file) / (1024 * 1024)
            
            logger.info(f"Analyzed video: {video_file}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze video: {e}")
            return {'error': str(e)}
    
    def compare_videos(self, video_files: List[str]) -> Dict[str, Any]:
        """Compare multiple videos
        
        Args:
            video_files: List of video file paths
            
        Returns:
            Comparison results
        """
        analyses = []
        
        for video_file in video_files:
            analysis = self.analyze_video(video_file)
            analyses.append(analysis)
        
        # Calculate statistics
        durations = [a.get('duration', 0) for a in analyses if 'duration' in a]
        file_sizes = [a.get('file_size_mb', 0) for a in analyses if 'file_size_mb' in a]
        
        comparison = {
            'videos': analyses,
            'summary': {
                'total_videos': len(analyses),
                'total_duration': sum(durations),
                'avg_duration': sum(durations) / len(durations) if durations else 0,
                'total_size_mb': sum(file_sizes),
                'avg_size_mb': sum(file_sizes) / len(file_sizes) if file_sizes else 0
            }
        }
        
        return comparison
    
    def get_recommendations(self, video_file: str) -> List[str]:
        """Get recommendations for video optimization
        
        Args:
            video_file: Path to video file
            
        Returns:
            List of recommendations
        """
        analysis = self.analyze_video(video_file)
        recommendations = []
        
        # Duration recommendations
        duration = analysis.get('duration', 0)
        if duration > 600:  # > 10 minutes
            recommendations.append("Consider splitting long videos into shorter segments for better engagement")
        elif duration < 10:  # < 10 seconds
            recommendations.append("Short videos perform well on social media platforms")
        
        # Resolution recommendations
        size = analysis.get('size', (0, 0))
        if size[0] < 1280:
            recommendations.append("Consider increasing resolution for better quality")
        
        # File size recommendations
        file_size = analysis.get('file_size_mb', 0)
        if file_size > 100:
            recommendations.append("Consider compressing to reduce file size for faster loading")
        
        # Audio recommendations
        if not analysis.get('has_audio', False):
            recommendations.append("Adding audio can improve engagement")
        
        return recommendations
    
    def generate_report(self, video_file: str, output_file: str) -> bool:
        """Generate a detailed analysis report
        
        Args:
            video_file: Path to video file
            output_file: Path to output report
            
        Returns:
            True if successful
        """
        analysis = self.analyze_video(video_file)
        recommendations = self.get_recommendations(video_file)
        
        try:
            # Generate report
            report = f"""Video Analytics Report
========================

File: {analysis.get('file', 'N/A')}
Duration: {analysis.get('duration', 0):.2f} seconds
FPS: {analysis.get('fps', 0)}
Resolution: {analysis.get('size', (0, 0))[0]}x{analysis.get('size', (0, 0))[1]}
Aspect Ratio: {analysis.get('aspect_ratio', 0):.2f}
File Size: {analysis.get('file_size_mb', 0):.2f} MB
Has Audio: {analysis.get('has_audio', False)}

Recommendations:
"""
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
            
            # Save report
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(report)
            
            logger.info(f"Generated report: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return False
    
    def batch_analyze(self, directory: str, pattern: str = "*.mp4") -> List[Dict[str, Any]]:
        """Analyze all videos in a directory
        
        Args:
            directory: Directory containing videos
            pattern: File pattern to match
            
        Returns:
            List of analysis results
        """
        results = []
        
        try:
            video_files = list(Path(directory).glob(pattern))
            
            for video_file in video_files:
                analysis = self.analyze_video(str(video_file))
                results.append(analysis)
            
            logger.info(f"Analyzed {len(results)} videos in {directory}")
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
        
        return results


def get_video_analytics(config: Optional[Dict[str, Any]] = None) -> VideoAnalytics:
    """Get a VideoAnalytics instance
    
    Args:
        config: Configuration dictionary
        
    Returns:
        VideoAnalytics instance
    """
    return VideoAnalytics(config)


__all__ = ['VideoAnalytics', 'get_video_analytics']
