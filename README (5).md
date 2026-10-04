# Text-to-Speech Converter

A single-file Python app that converts text to speech. It has a simple desktop GUI and a command-line interface, and supports two engines:

| Engine | Library | Internet | Output format | Notes |
|--------|---------|----------|---------------|-------|
| Offline | `pyttsx3` | Not needed | WAV (platform dependent) | Uses your OS voices; adjustable speed, volume, voice |
| Online | `gTTS` | Required | MP3 | Google voices; many languages (e.g. `en`, `ta`, `hi`) |

## Features

- GUI built with Tkinter (no extra install needed on most Python setups)
- Type text or load a `.txt` file
- Speak aloud or save to an audio file
- Choose voice, speed and volume (offline engine)
- Choose language and slow mode (online engine)
- Stop button for offline speech
- Full CLI for scripting

## Requirements

- Python 3.8+
- Tkinter (bundled with Python on Windows/macOS; on Debian/Ubuntu: `sudo apt install python3-tk`)
- On Linux, the offline engine needs eSpeak: `sudo apt install espeak-ng`

## Installation

```bash
pip install pyttsx3 gTTS
```

You can install only one of them if you just need one engine.

## Usage

### GUI

```bash
python tts_converter.py
```

1. Type text or click **Open .txt**
2. Pick the engine, voice, speed, volume or language
3. Click **Speak** or **Save audio**

### Command line

```bash
# Speak with the offline engine
python tts_converter.py --text "Hello, world!"

# List available offline voices
python tts_converter.py --list-voices

# Offline, custom speed, save to file
python tts_converter.py --text "Good morning" --rate 150 --out hello.wav

# Online, Tamil, read from file, save as MP3
python tts_converter.py --file notes.txt --engine online --lang ta --out notes.mp3
```

### Options

| Option | Description |
|--------|-------------|
| `--text` | Text to speak |
| `--file` | Read text from a file |
| `--engine` | `offline` (default) or `online` |
| `--out` | Save audio to a path instead of playing |
| `--rate` | Speech speed, offline only (default 170) |
| `--volume` | 0.0 to 1.0, offline only |
| `--voice` | Voice id from `--list-voices`, offline only |
| `--lang` | Language code, online only (default `en`) |
| `--slow` | Slower speech, online only |
| `--gui` | Force-launch the GUI |

## Troubleshooting

- **"pyttsx3 is not installed"**: run `pip install pyttsx3`.
- **No sound on Linux**: install `espeak-ng` and check your audio output.
- **Online engine fails**: check your internet connection and that the language code is valid.
- **Online "Speak" opens another app**: gTTS can't stream, so it creates an MP3 and opens it in your default media player.
- **Saved offline file format**: depends on the OS speech backend (SAPI5 on Windows, NSSpeech on macOS, eSpeak on Linux). WAV is the safest choice.

## Project structure

```
.
├── tts_converter.py   # the whole app
└── README.md
```

## License

MIT, free to use and modify.
