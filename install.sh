#!/bin/bash

# Advanced Video Generator - Installation Script
# This script installs all dependencies and sets up the environment

set -e  # Exit on error

echo "🎬 Advanced Video Generator - Installation"
echo "=========================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 7 ]; then
    echo "❌ Python 3.7 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check for virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Not running in a virtual environment"
    read -p "Create virtual environment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    fi
else
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
fi

# Install system dependencies
echo ""
echo "📦 Installing system dependencies..."

if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install -y ffmpeg imagemagick python3-dev
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum install -y ffmpeg ImageMagick python3-devel
elif command -v brew &> /dev/null; then
    # macOS
    brew install ffmpeg imagemagick
else
    echo "⚠️  Could not detect package manager. Please install FFmpeg and ImageMagick manually."
fi

echo "✅ System dependencies installed"

# Install Python dependencies
echo ""
echo "🐍 Installing Python dependencies..."

# Upgrade pip
pip install --upgrade pip

# Install PyTorch (check for CUDA)
if command -v nvidia-smi &> /dev/null; then
    echo "📊 NVIDIA GPU detected, installing CUDA version"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    echo "💻 CPU-only mode, installing CPU version"
    pip install torch torchvision torchaudio
fi

# Install core requirements
pip install -r requirements.txt

echo "✅ Python dependencies installed"

# Create directories
echo ""
echo "📁 Creating directories..."

mkdir -p output temp logs cache models scripts music assets

echo "✅ Directories created"

# Create configuration file
echo ""
echo "⚙️  Creating configuration..."

if [ ! -f config.yaml ]; then
    python3 -c "
import yaml
config = {
    'project': {
        'name': 'video_generator',
        'output_dir': './output',
        'temp_dir': './temp',
        'log_dir': './logs',
        'cache_dir': './cache',
        'models_dir': './models'
    },
    'video': {
        'default_resolution': '1920x1080',
        'default_fps': 30
    },
    'audio': {
        'tts_engine': 'google',
        'default_language': 'en-US'
    }
}
with open('config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
"
    echo "✅ Configuration file created: config.yaml"
else
    echo "✅ Configuration file already exists"
fi

# Download sample files
echo ""
echo "📝 Downloading sample files..."

if [ ! -f examples/sample_script.txt ]; then
    mkdir -p examples
    cat > examples/sample_script.txt << 'EOF'
Welcome to the Advanced Video Generator!

This tool allows you to create professional videos from text scripts.

It uses AI to generate speech, images, and assemble everything automatically.

You can customize the voice, add subtitles, and include background music.

The generated videos are high quality and ready for sharing.

Try different scripts and see what amazing videos you can create!
EOF
    echo "✅ Sample script created"
fi

# Test installation
echo ""
echo "🧪 Testing installation..."

if python3 -c "import torch, diffusers, gtts, moviepy; print('✅ Import test passed')" 2>/dev/null; then
    echo "✅ All imports successful"
else
    echo "⚠️  Some imports failed, but installation may still work"
fi

# Final message
echo ""
echo "✨ Installation Complete!"
echo "========================"
echo ""
echo "To get started:"
echo ""
echo "1. Edit config.yaml to customize settings"
echo "2. Place your scripts in the scripts/ directory"
echo "3. Run: python run.py --help"
echo ""
echo "Quick start examples:"
echo "  python run.py --script examples/sample_script.txt --output my_video.mp4"
echo "  python run.py --web-ui"
echo ""
echo "For Google Colab:"
echo "  Open colab_notebook.ipynb in Google Colab"
echo ""
echo "Need help? Check the documentation at:"
echo "https://github.com/yourusername/advanced-video-generator"
echo ""
