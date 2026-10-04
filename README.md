# 🔊 Text to Speech Converter

A simple Python tool that converts typed text or a text file into spoken audio. It supports online speech with Google's gTTS (saves an MP3) and offline speech with pyttsx3 (plays through your speakers).

## Features

- Convert typed text or a `.txt` file to speech
- Save the speech as an MP3 file (gTTS)
- Speak out loud without internet (pyttsx3)
- Choose the language (English, Hindi, Tamil, and more)
- Simple command-line interface

## Requirements

- Python 3.8 or higher
- [gTTS](https://pypi.org/project/gTTS/) (needs an internet connection)
- [pyttsx3](https://pypi.org/project/pyttsx3/) (works offline)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/text-to-speech-converter.git
cd text-to-speech-converter
```

2. Install the dependencies:

```bash
pip install gTTS pyttsx3
```

## Usage

### Convert text to an MP3 file

```bash
python text_to_speech.py --text "Hello, welcome to my project" --output hello.mp3
```

### Convert a text file to an MP3 file

```bash
python text_to_speech.py --file speech.txt --output speech.mp3
```

### Choose a language

```bash
python text_to_speech.py --text "வணக்கம்" --lang ta --output tamil.mp3
```

### Speak out loud (offline)

```bash
python text_to_speech.py --text "Hello world" --offline
```

## Command-Line Options

| Option | Description | Default |
|---|---|---|
| `--text` | Text to convert | None |
| `--file` | Path to a `.txt` file to convert | None |
| `--lang` | Language code (`en`, `hi`, `ta`, `fr`, ...) | `en` |
| `--output` | Output MP3 filename | `output.mp3` |
| `--offline` | Use pyttsx3 and speak out loud instead of saving a file | Off |

## How It Works

1. Reads the text from the command line or a file.
2. **Online
