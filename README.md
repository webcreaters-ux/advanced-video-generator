# 🎬 Advanced Video Generator

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/webcreaters-ux/advanced-video-generator/blob/main/colab_notebook.ipynb)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/webcreaters-ux/advanced-video-generator.svg?style=social)](https://github.com/webcreaters-ux/advanced-video-generator/stargazers)
[![Deploy to GitHub Pages](https://github.com/webcreaters-ux/advanced-video-generator/actions/workflows/deploy.yml/badge.svg)](https://github.com/webcreaters-ux/advanced-video-generator/actions/workflows/deploy.yml)

**Generate professional videos from scripts using AI-powered tools** - Text-to-Speech, AI Image Generation, Automatic Subtitles, and more!

🌐 **Live Demo**: [https://webcreaters-ux.github.io/advanced-video-generator](https://webcreaters-ux.github.io/advanced-video-generator)

## ✨ Features

- 🎤 **Multiple TTS Engines**: Google, Microsoft Edge, Coqui TTS, pyttsx3
- 🖼️ **AI Image Generation**: Stable Diffusion, DALL-E Mini, CLIP
- 📝 **Smart Script Processing**: Automatic scene splitting, AI enhancement
- 🎞️ **Professional Video Editing**: Transitions, subtitles, background music
- ☁️ **Cloud Integration**: Google Drive, Colab optimized
- 🎮 **Interactive UI**: Web interface and Colab widgets
- ⚡ **GPU Acceleration**: Fast AI processing with CUDA
- 🔄 **Batch Processing**: Generate multiple videos at once
- 🔐 **Page Activation**: Secure client ID/secret authentication

## 🚀 Quick Start

### Google Colab (Recommended)
Click the button below to launch in Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/webcreaters-ux/advanced-video-generator/blob/main/colab_notebook.ipynb)

```python
# In Google Colab notebook
!git clone https://github.com/webcreaters-ux/advanced-video-generator.git
%cd advanced-video-generator

# Use the interactive UI
from advanced_video_generator.ui.colab_ui import ColabVideoGeneratorUI
ui = ColabVideoGeneratorUI()
ui.display()
```

### Local Installation

#### Option 1: Using Installation Script (Linux/macOS)
```bash
# Clone and setup
git clone https://github.com/webcreaters-ux/advanced-video-generator.git
cd advanced-video-generator

# Run installation script
chmod +x install.sh
./install.sh
```

#### Option 2: Manual Installation
```bash
# Clone repository
git clone https://github.com/webcreaters-ux/advanced-video-generator.git
cd advanced-video-generator

# Install PyTorch with CUDA support (if you have NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Or install CPU-only version
pip install torch torchvision torchaudio

# Install other dependencies
pip install -r requirements.txt

# Run the application
python run.py --web-ui
```

### Page Activation

The web interface requires activation using client credentials:

**Demo Credentials:**
- Client ID: `demo_user`
- Client Secret: `demo_secret_123`

To generate new credentials, use the Python API:
```python
from advanced_video_generator.auth import get_auth_manager

auth = get_auth_manager()
client_id, client_secret = auth.generate_credentials(name="My App", expires_in_days=30)
print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")
```

## 📖 Usage Examples

### Simple Colab Usage

```python
from advanced_video_generator import ColabVideoGenerator

# Initialize generator
generator = ColabVideoGenerator()

# Generate video from script
generator.generate_from_script(
    script_text="Your script here...",
    output_name="my_video.mp4",
    generate_images=True,
    add_subtitles=True
)

# Download in Colab
generator.download_video()

# Save to Google Drive
generator.save_to_drive()
```

### Advanced Usage

```python
from advanced_video_generator import (
    ColabVideoGenerator,
    quick_generate
)

# Quick one-liner generation
result = quick_generate(
    "Welcome to AI video generation!",
    output_name="quick.mp4"
)

# Custom configuration
generator = ColabVideoGenerator(
    output_dir="./videos",
    quality="high",
    tts_engine="edge",
    language="en-US"
)

# Generate with all options
generator.generate_from_script(
    script_text="""
    Welcome to the world of AI!
    Today we explore amazing technologies.
    """,
    output_name="presentation.mp4",
    quality="high",
    generate_images=True,
    add_subtitles=True,
    add_transitions=True
)
```

## 🌐 GitHub Pages Deployment

This project includes a beautiful landing page that can be deployed to GitHub Pages for free!

### Automatic Deployment

1. **Fork or clone this repository** to your GitHub account

2. **Enable GitHub Pages**:
   - Go to your repository settings
   - Navigate to "Pages" in the sidebar
   - Under "Source", select "GitHub Actions"

3. **Push to main branch**:
   - The workflow in `.github/workflows/deploy.yml` will automatically deploy your site
   - Your site will be available at: `https://webcreaters-ux.github.io/advanced-video-generator`

### Manual Deployment

If you prefer to deploy manually:

1. Go to repository **Settings** → **Pages**
2. Set Source to "Deploy from a branch"
3. Select "main" branch and "/ (root)" folder
4. Click Save

### Custom Domain (Optional)

To use a custom domain:

1. Add a `CNAME` file with your domain name
2. Configure DNS records with your domain provider
3. Enable HTTPS in repository settings

## 📁 Project Structure

```
advanced-video-generator/
├── index.html              # Landing page
├── css/
│   └── style.css          # Styles
├── js/
│   └── app.js             # JavaScript functionality
├── assets/
│   └── favicon.svg        # Favicon
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Pages deployment
├── advanced_video_generator/
│   ├── main.py            # Core video generation
│   ├── tts_generator.py   # Text-to-speech
│   ├── config.py          # Configuration
│   └── ui/
│       └── colab_ui.py    # Colab interface
├── run.py                 # CLI entry point
├── requirements.txt       # Python dependencies
└── config.yaml           # Configuration file
```
