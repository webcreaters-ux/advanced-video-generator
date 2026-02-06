from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="advanced-video-generator",
    version="1.0.0",
    author="Advanced Video Generator Team",
    author_email="your.email@example.com",
    description="Generate professional videos from scripts using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/advanced-video-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "video-generator=advanced_video_generator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "advanced_video_generator": ["configs/*.yaml", "ui/templates/*"],
    },
    keywords="video generation ai tts stable-diffusion moviepy",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/advanced-video-generator/issues",
        "Source": "https://github.com/yourusername/advanced-video-generator",
        "Documentation": "https://github.com/yourusername/advanced-video-generator/docs",
    },
)
