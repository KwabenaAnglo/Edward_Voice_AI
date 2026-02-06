from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="edward-voice-ai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A voice-enabled AI assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/edward-voice-ai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "sounddevice>=0.4.6",
        "scipy>=1.10.0",
        "elevenlabs>=0.2.26",
        "webrtcvad-wheels>=2.0.10",
        "pyaudio>=0.2.13",
        "numpy>=1.25.2",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "keyboard>=0.13.5",
        "pyttsx3>=2.90",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=0.910",
            "pylint>=2.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "edward-ai=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
)
