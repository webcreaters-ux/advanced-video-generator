from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="advanced-video-generator",
    version="1.0.0",
    author="WebCreators-UX",
    author_email="info@webcreators.ux",
    description="Generate professional videos from scripts using AI-powered tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/webcreaters-ux/advanced-video-generator",
    project_urls={
        "Bug Tracker": "https://github.com/webcreaters-ux/advanced-video-generator/issues",
        "Documentation": "https://github.com/webcreaters-ux/advanced-video-generator#readme",
        "Source Code": "https://github.com/webcreaters-ux/advanced-video-generator",
        "Tracker": "https://github.com/webcreaters-ux/advanced-video-generator/issues",
    },
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Conversion",
        "Topic :: Multimedia :: Video :: Animation",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: Mac OS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "pre-commit>=3.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "video-generator=run:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="video generation ai tts stable-diffusion moviepy text-to-speech image-generation",
    platforms=["any"],
)
