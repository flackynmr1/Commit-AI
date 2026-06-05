# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
JARVIS FREE AI VIDEO SYSTEM is a 100% gratis lokalt system för att skapa AI-förklaringsvideos. The system creates business explanation videos from text or voice input using local AI tools.

## Core Architecture
The system follows a modular pipeline architecture:
1. **Input Processing** - Voice/text commands handled by `main.py`
2. **Script Generation** - Business scripts created by `script_writer.py` 
3. **Text-to-Speech** - Swedish voice generation via `tts_edge.py` (Edge TTS)
4. **Video Creation** - Two paths:
   - Simple slide videos with `simple_video.py` (MoviePy + text overlays)
   - Avatar videos via `sadtalker_runner.py` (when SadTalker is installed)
5. **Configuration** - Centralized settings in `config.py`

## Key Components

### Main Entry Points
- `main.py` - Primary Jarvis interface with voice/text command loop
- `free_video_agent.py` - Standalone video creation agent
- `run_*.py` - Various utility scripts for specific functionalities

### Core Modules
- `script_writer.py` - Generates business video scripts from ideas
- `tts_edge.py` - Creates Swedish speech using Microsoft Edge TTS
- `simple_video.py` - Creates MP4 videos with text slides + audio (MoviePy)
- `sadtalker_runner.py` - Optional avatar video generation (requires separate SadTalker installation)
- `calendar_tools.py` - Google Calendar integration
- `spotify.py` - Spotify integration
- `memory.py` - Conversation memory system
- `agent.py` - Base agent framework

## Development Commands

### Setup
```bash
# Clone/repository setup already done
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install edge-tts moviepy pillow requests

# For moviepy issues:
pip install moviepy==1.0.3
```

### Running the System
```bash
# Start interactive Jarvis
python main.py

# Test video creation directly
python free_video_agent.py

# Say/write command in Jarvis interface:
skapa video om min business idea
```

### Video Output
- Generated videos saved to `videos/` directory
- Audio files stored in `audio/` directory  
- Temporary outputs in `outputs/` directory
- Avatar image (if using SadTalker): `assets\avatar.png`

### SadTalker Setup (Optional)
For avatar videos:
1. Install SadTalker separately in `C:\Users\46730\Desktop\JARVIS\SadTalker`
2. Place avatar image at `assets\avatar.png`
3. System automatically detects and uses SadTalker when available

## Configuration
- Voice settings in `config.py` (VOICE = "sv-SE-MattiasNeural" by default)
- Directory paths configured in `config.py`
- SadTalker toggle: `USE_SADTALKER_IF_AVAILABLE = True`

## File Organization
```
JARVIS/
├── main.py                 # Main Jarvis interface
├── free_video_agent.py     # Standalone video creator
├── script_writer.py        # Script generation
├── tts_edge.py             # Text-to-speech (Edge TTS)
├── simple_video.py         # Basic video creation (MoviePy)
├── sadtalker_runner.py     # Avatar video (optional)
├── config.py               # Paths and settings
├── calendar_tools.py       # Google Calendar
├── spotify.py              # Spotify integration
├── memory.py               # Conversation memory
├── agent.py                # Base agent class
├── videos/                 # Output videos
├── audio/                  # Generated audio
├── assets/                 # Avatar image (avatar.png)
├── outputs/                # Temporary files
└── SadTalker/              # Optional SadTalker installation
```

## Notes
- System is 100% free and runs completely locally
- Requires internet only for initial package downloads
- Voice generation uses free Microsoft Edge TTS
- Video creation uses MoviePy for slide-based videos
- Avatar videos require separate SadTalker/Wav2Lip installation
- All processing happens locally on user's machine
- Supports Swedish language primarily (sv-SE voices)