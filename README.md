# 🎬 Advanced Video Generator

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourusername/advanced-video-generator/blob/main/colab_notebook.ipynb)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/advanced-video-generator.svg?style=social)](https://github.com/yourusername/advanced-video-generator/stargazers)
[![Deploy to GitHub Pages](https://github.com/yourusername/advanced-video-generator/actions/workflows/deploy.yml/badge.svg)](https://github.com/yourusername/advanced-video-generator/actions/workflows/deploy.yml)

**Generate professional videos from scripts using AI-powered tools** - Text-to-Speech, AI Image Generation, Automatic Subtitles, and more!

🌐 **Live Demo**: [https://yourusername.github.io/advanced-video-generator](https://yourusername.github.io/advanced-video-generator)

## ✨ Features

- 🎤 **Multiple TTS Engines**: Google, Microsoft Edge, Coqui TTS, pyttsx3
- 🖼️ **AI Image Generation**: Stable Diffusion, DALL-E Mini, CLIP
- 📝 **Smart Script Processing**: Automatic scene splitting, AI enhancement
- 🎞️ **Professional Video Editing**: Transitions, subtitles, background music
- ☁️ **Cloud Integration**: Google Drive, Colab optimized
- 🎮 **Interactive UI**: Web interface and Colab widgets
- ⚡ **GPU Acceleration**: Fast AI processing with CUDA
- 🔄 **Batch Processing**: Generate multiple videos at once

## 🚀 Quick Start

### Google Colab (Recommended)
Click the button below to launch in Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourusername/advanced-video-generator/blob/main/colab_notebook.ipynb)

### Local Installation
```bash
# Clone repository
git clone https://github.com/yourusername/advanced-video-generator.git
cd advanced-video-generator

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py --web-ui
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
   - Your site will be available at: `https://yourusername.github.io/advanced-video-generator`

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
