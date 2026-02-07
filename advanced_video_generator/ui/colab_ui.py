"""
Google Colab UI for video generator
"""

import os
import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

from ..main import AdvancedVideoGenerator, GenerationOptions, VideoQuality
from ..cloud_manager import CloudManager

logger = logging.getLogger(__name__)

class ColabVideoGeneratorUI:
    """Interactive UI for Google Colab"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize UI
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.generator = None
        self.cloud = CloudManager()
        self.current_video_path = None
        
        # Create widgets
        self._create_widgets()
        
        # Connect events
        self._connect_events()
        
        logger.info("Colab UI initialized")
    
    def _create_widgets(self):
        """Create all UI widgets"""
        
        # Header
        self.header = widgets.HTML(
            "<h1 style='color: #4285f4;'>🎬 Advanced Video Generator</h1>"
            "<h3>Generate professional videos from scripts using AI</h3>"
        )
        
        # Script input
        self.script_input = widgets.Textarea(
            value=self._get_sample_script(),
            placeholder='Enter your script here...',
            description='Script:',
            layout=widgets.Layout(width='100%', height='200px'),
            style={'description_width': 'initial'}
        )
        
        # Options panel
        self.output_name = widgets.Text(
            value='my_video.mp4',
            description='Output name:',
            layout=widgets.Layout(width='300px')
        )
        
        self.quality = widgets.Dropdown(
            options=[
                (q.value.capitalize(), q) 
                for q in VideoQuality
            ],
            value=VideoQuality.MEDIUM,
            description='Quality:'
        )
        
        self.tts_engine = widgets.Dropdown(
            options=['google', 'edge', 'coqui', 'pyttsx3'],
            value='google',
            description='TTS Engine:'
        )
        
        self.image_generation = widgets.Checkbox(
            value=True,
            description='Generate AI Images'
        )
        
        self.add_subtitles = widgets.Checkbox(
            value=True,
            description='Add Subtitles'
        )
        
        self.add_transitions = widgets.Checkbox(
            value=True,
            description='Add Transitions'
        )
        
        # Control buttons
        self.generate_btn = widgets.Button(
            description='🚀 Generate Video',
            button_style='success',
            icon='play',
            layout=widgets.Layout(width='150px', height='40px')
        )
        
        self.download_btn = widgets.Button(
            description='📥 Download',
            button_style='info',
            icon='download',
            disabled=True,
            layout=widgets.Layout(width='120px', height='40px')
        )
        
        self.save_drive_btn = widgets.Button(
            description='💾 Save to Drive',
            button_style='warning',
            icon='save',
            disabled=True,
            layout=widgets.Layout(width='140px', height='40px')
        )
        
        self.clear_btn = widgets.Button(
            description='🗑️ Clear',
            button_style='danger',
            icon='trash',
            layout=widgets.Layout(width='100px', height='40px')
        )
        
        # Progress indicator
        self.progress = widgets.IntProgress(
            value=0,
            min=0,
            max=100,
            description='Progress:',
            bar_style='info',
            style={'bar_color': '#4285f4'},
            layout=widgets.Layout(width='100%')
        )
        
        # Status output
        self.status_output = widgets.Output()
        
        # Video preview
        self.video_preview = widgets.Output()
        
        # Create layouts
        self.options_box = widgets.VBox([
            widgets.HTML("<h4>Options:</h4>"),
            self.output_name,
            self.quality,
            self.tts_engine,
            self.image_generation,
            self.add_subtitles,
            self.add_transitions
        ])
        
        self.control_box = widgets.HBox([
            self.generate_btn,
            self.download_btn,
            self.save_drive_btn,
            self.clear_btn
        ])
        
        # Main UI layout
        self.ui = widgets.VBox([
            self.header,
            widgets.HTML("<hr>"),
            self.script_input,
            widgets.HTML("<br>"),
            self.options_box,
            widgets.HTML("<br>"),
            self.progress,
            self.control_box,
            widgets.HTML("<hr>"),
            self.status_output,
            self.video_preview
        ])
    
    def _connect_events(self):
        """Connect widget events to handlers"""
        self.generate_btn.on_click(self._on_generate_click)
        self.download_btn.on_click(self._on_download_click)
        self.save_drive_btn.on_click(self._on_save_drive_click)
        self.clear_btn.on_click(self._on_clear_click)
    
    def display(self):
        """Display the UI"""
        display(self.ui)
    
    def _on_generate_click(self, button):
        """Handle generate button click"""
        with self.status_output:
            clear_output()
            
            try:
                # Update progress
                self.progress.value = 10
                
                # Initialize generator if needed
                if self.generator is None:
                    self._update_status("Initializing video generator...")
                    self.generator = AdvancedVideoGenerator(self.config_path)
                    self.progress.value = 20
                
                # Create generation options
                options = GenerationOptions(
                    quality=self.quality.value,
                    voice_engine=self.tts_engine.value,
                    generate_images=self.image_generation.value,
                    add_subtitles=self.add_subtitles.value,
                    add_transitions=self.add_transitions.value
                )
                
                # Generate video
                self._update_status("Starting video generation...")
                self.progress.value = 30
                
                result = self.generator.generate_from_script(
                    script_text=self.script_input.value,
                    output_path=f"./output/{self.output_name.value}",
                    options=options
                )
                
                self.progress.value = 90
                
                if result['success']:
                    self.current_video_path = result['output_path']
                    self._update_status(
                        f"✅ Video generated successfully!\n"
                        f"Duration: {result['duration']:.1f}s\n"
                        f"Time: {result['generation_time']:.1f}s"
                    )
                    
                    # Enable download buttons
                    self.download_btn.disabled = False
                    self.save_drive_btn.disabled = False
                    
                    # Show preview
                    self._show_video_preview()
                    
                else:
                    self._update_status(
                        f"❌ Generation failed: {result.get('error', 'Unknown error')}"
                    )
                
                self.progress.value = 100
                
            except Exception as e:
                self._update_status(f"❌ Error: {str(e)}")
                logger.error(f"Generation failed: {e}", exc_info=True)
                self.progress.value = 0
    
    def _on_download_click(self, button):
        """Handle download button click"""
        if self.current_video_path and os.path.exists(self.current_video_path):
            from google.colab import files
            files.download(self.current_video_path)
            self._update_status("📥 Download started...")
    
    def _on_save_drive_click(self, button):
        """Handle save to Google Drive click"""
        if self.current_video_path and os.path.exists(self.current_video_path):
            try:
                self.cloud.mount_google_drive()
                
                drive_path = f"/content/drive/MyDrive/VideoGenerator/{os.path.basename(self.current_video_path)}"
                success = self.cloud.save_to_drive(self.current_video_path, drive_path)
                
                if success:
                    self._update_status(f"✅ Saved to Google Drive: {drive_path}")
                else:
                    self._update_status("❌ Failed to save to Google Drive")
                    
            except Exception as e:
                self._update_status(f"❌ Error saving to Drive: {e}")
    
    def _on_clear_click(self, button):
        """Handle clear button click"""
        self.script_input.value = ""
        self.output_name.value = "my_video.mp4"
        self.current_video_path = None
        self.download_btn.disabled = True
        self.save_drive_btn.disabled = True
        
        with self.status_output:
            clear_output()
        
        with self.video_preview:
            clear_output()
        
        self.progress.value = 0
        self._update_status("Cleared all inputs")
    
    def _show_video_preview(self):
        """Show video preview in notebook"""
        if not self.current_video_path or not os.path.exists(self.current_video_path):
            return
        
        with self.video_preview:
            clear_output()
            
            # Read video file
            try:
                with open(self.current_video_path, 'rb') as f:
                    video_data = f.read()
                
                # Convert to base64
                video_b64 = base64.b64encode(video_data).decode()
                
                # Create HTML video element
                video_html = f"""
                <h4>Video Preview:</h4>
                <video width="640" controls style="border: 2px solid #4285f4; border-radius: 8px;">
                    <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <p><small>File: {os.path.basename(self.current_video_path)}</small></p>
                """
                
                display(HTML(video_html))
                
            except Exception as e:
                self._update_status(f"❌ Failed to show preview: {e}")
    
    def _update_status(self, message: str):
        """Update status message"""
        with self.status_output:
            print(message)
    
    def _get_sample_script(self) -> str:
        """Get sample script"""
        return """Welcome to the world of artificial intelligence!

Today, we explore how AI is revolutionizing various industries.

From healthcare to finance, AI is making systems smarter and more efficient.

Machine learning algorithms can analyze vast amounts of data.

They identify patterns that humans might never notice.

Natural language processing allows computers to understand human language.

Computer vision enables machines to see and interpret visual information.

The future is here, and it's powered by artificial intelligence.

Let's build a better tomorrow together with AI!"""

    def batch_generate_ui(self):
        """Create batch generation UI"""
        batch_ui = widgets.VBox([
            widgets.HTML("<h3>Batch Generation</h3>"),
            widgets.FileUpload(
                accept='.txt',
                multiple=True,
                description='Upload scripts'
            ),
            widgets.Button(
                description='Process All',
                button_style='primary'
            ),
            widgets.Output()
        ])
        
        return batch_ui
    
    def settings_ui(self):
        """Create settings UI"""
        settings_ui = widgets.VBox([
            widgets.HTML("<h3>Settings</h3>"),
            widgets.Accordion(children=[
                widgets.VBox([
                    widgets.Text(
                        description='Output Directory:',
                        value='./output'
                    ),
                    widgets.Text(
                        description='Temp Directory:',
                        value='./temp'
                    )
                ]),
                widgets.VBox([
                    widgets.Checkbox(
                        description='Use GPU Acceleration',
                        value=True
                    ),
                    widgets.IntSlider(
                        description='Max Workers:',
                        min=1,
                        max=8,
                        value=4
                    )
                ])
            ]),
            widgets.Button(
                description='Save Settings',
                button_style='info'
            )
        ])
        
        settings_ui.children[1].set_title(0, 'Directories')
        settings_ui.children[1].set_title(1, 'Performance')
        
        return settings_ui

# Utility function for quick UI creation
def launch_ui(config_path: Optional[str] = None):
    """Launch the Colab UI
    
    Args:
        config_path: Path to configuration file
    """
    ui = ColabVideoGeneratorUI(config_path)
    ui.display()
    return ui

__all__ = ['ColabVideoGeneratorUI', 'launch_ui']
