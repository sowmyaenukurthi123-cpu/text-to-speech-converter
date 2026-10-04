#!/usr/bin/env python3
"""
Text-to-Speech Converter (single file)

Two engines:
  * offline : pyttsx3  (uses your OS voices, no internet needed)
  * online  : gTTS     (Google TTS, needs internet, saves MP3)

Usage:
  python tts_converter.py                          # launch GUI
  python tts_converter.py --text "Hello world"     # speak with offline engine
  python tts_converter.py --file notes.txt --engine online --lang ta --out notes.mp3
  python tts_converter.py --list-voices
"""

import argparse
import os
import subprocess
import sys
import tempfile
import threading

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from gtts import gTTS
except ImportError:
    gTTS = None


# --------------------------------------------------------------------------
# Core TTS logic
# --------------------------------------------------------------------------
class TTSConverter:
    """Wraps both engines behind one small API."""

    def __init__(self):
        self._engine = None  # active pyttsx3 engine (for stopping)

    # ---------- offline (pyttsx3) ----------
    @staticmethod
    def list_voices():
        if pyttsx3 is None:
            raise RuntimeError("pyttsx3 is not installed. Run: pip install pyttsx3")
        engine = pyttsx3.init()
        voices = [(v.id, v.name) for v in engine.getProperty("voices")]
        engine.stop()
        return voices

    def _make_engine(self, rate, volume, voice_id):
        if pyttsx3 is None:
            raise RuntimeError("pyttsx3 is not installed. Run: pip install pyttsx3")
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)
        if voice_id:
            engine.setProperty("voice", voice_id)
        return engine

    def speak_offline(self, text, rate=170, volume=1.0, voice_id=None):
        engine = self._make_engine(rate, volume, voice_id)
        self._engine = engine
        engine.say(text)
        engine.runAndWait()
        self._engine = None

    def save_offline(self, text, path, rate=170, volume=1.0, voice_id=None):
        engine = self._make_engine(rate, volume, voice_id)
        engine.save_to_file(text, path)
        engine.runAndWait()

    # ---------- online (gTTS) ----------
    @staticmethod
    def save_online(text, path, lang="en", slow=False):
        if gTTS is None:
            raise RuntimeError("gTTS is not installed. Run: pip install gTTS")
        gTTS(text=text, lang=lang, slow=slow).save(path)

    def speak_online(self, text, lang="en", slow=False):
        """gTTS can't stream, so save a temp MP3 and open it in the default player."""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        self.save_online(text, tmp.name, lang, slow)
        open_with_default_player(tmp.name)

    # ---------- control ----------
    def stop(self):
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                pass


def open_with_default_player(path):
    if sys.platform.startswith("win"):
        os.startfile(path)  # noqa
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


# --------------------------------------------------------------------------
# GUI (tkinter)
# --------------------------------------------------------------------------
def run_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    tts = TTSConverter()

    root = tk.Tk()
    root.title("Text to Speech Converter")
    root.geometry("640x560")
    root.minsize(520, 480)

    pad = {"padx": 10, "pady": 5}

    # Text area
    ttk.Label(root, text="Enter text:").pack(anchor="w", **pad)
    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True, **pad)
    text_box = tk.Text(frame, wrap="word", height=10, font=("Segoe UI", 11))
    scroll = ttk.Scrollbar(frame, command=text_box.yview)
    text_box.configure(yscrollcommand=scroll.set)
    text_box.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    # Engine selection
    engine_var = tk.StringVar(value="offline")
    eng_frame = ttk.LabelFrame(root, text="Engine")
    eng_frame.pack(fill="x", **pad)
    ttk.Radiobutton(eng_frame, text="Offline (pyttsx3)", value="offline",
                    variable=engine_var).pack(side="left", padx=10, pady=5)
    ttk.Radiobutton(eng_frame, text="Online (gTTS)", value="online",
                    variable=engine_var).pack(side="left", padx=10, pady=5)

    # Settings
    opt = ttk.LabelFrame(root, text="Settings")
    opt.pack(fill="x", **pad)
    opt.columnconfigure(1, weight=1)

    ttk.Label(opt, text="Voice (offline):").grid(row=0, column=0, sticky="w", padx=8, pady=4)
    voice_var = tk.StringVar()
    voice_ids = {}
    voice_combo = ttk.Combobox(opt, textvariable=voice_var, state="readonly")
    voice_combo.grid(row=0, column=1, sticky="ew", padx=8, pady=4)
    try:
        for vid, name in TTSConverter.list_voices():
            voice_ids[name] = vid
        voice_combo["values"] = list(voice_ids)
        if voice_ids:
            voice_combo.current(0)
    except Exception:
        voice_combo["values"] = ["(no offline voices found)"]
        voice_combo.current(0)

    ttk.Label(opt, text="Speed:").grid(row=1, column=0, sticky="w", padx=8, pady=4)
    rate_var = tk.IntVar(value=170)
    ttk.Scale(opt, from_=80, to=300, variable=rate_var,
              command=lambda v: rate_var.set(int(float(v)))).grid(row=1, column=1, sticky="ew", padx=8)

    ttk.Label(opt, text="Volume:").grid(row=2, column=0, sticky="w", padx=8, pady=4)
    vol_var = tk.DoubleVar(value=1.0)
    ttk.Scale(opt, from_=0.0, to=1.0, variable=vol_var).grid(row=2, column=1, sticky="ew", padx=8)

    ttk.Label(opt, text="Language code (online):").grid(row=3, column=0, sticky="w", padx=8, pady=4)
    lang_var = tk.StringVar(value="en")
    ttk.Entry(opt, textvariable=lang_var, width=8).grid(row=3, column=1, sticky="w", padx=8)

    # Status bar
    status = tk.StringVar(value="Ready")
    ttk.Label(root, textvariable=status, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    # ---- helpers ----
    def get_text():
        t = text_box.get("1.0", "end").strip()
        if not t:
            messagebox.showwarning("No text", "Please enter some text first.")
        return t

    def run_async(fn, ok_msg):
        def worker():
            try:
                fn()
                root.after(0, lambda: status.set(ok_msg))
            except Exception as e:
                root.after(0, lambda: (status.set("Error"), messagebox.showerror("Error", str(e))))
        threading.Thread(target=worker, daemon=True).start()

    def current_voice():
        return voice_ids.get(voice_var.get())

    # ---- actions ----
    def on_speak():
        t = get_text()
        if not t:
            return
        status.set("Speaking...")
        if engine_var.get() == "offline":
            run_async(lambda: tts.speak_offline(t, rate_var.get(), vol_var.get(), current_voice()), "Done")
        else:
            run_async(lambda: tts.speak_online(t, lang_var.get().strip() or "en"), "Opened in player")

    def on_stop():
        tts.stop()
        status.set("Stopped")

    def on_save():
        t = get_text()
        if not t:
            return
        online = engine_var.get() == "online"
        ext = ".mp3" if online else ".wav"
        path = filedialog.asksaveasfilename(defaultextension=ext,
                                            filetypes=[("Audio", f"*{ext}"), ("All files", "*.*")])
        if not path:
            return
        status.set("Saving...")
        if online:
            run_async(lambda: tts.save_online(t, path, lang_var.get().strip() or "en"), f"Saved: {path}")
        else:
            run_async(lambda: tts.save_offline(t, path, rate_var.get(), vol_var.get(), current_voice()),
                      f"Saved: {path}")

    def on_open():
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text_box.delete("1.0", "end")
                text_box.insert("1.0", f.read())
            status.set(f"Loaded {os.path.basename(path)}")

    def on_clear():
        text_box.delete("1.0", "end")

    # Buttons
    btns = ttk.Frame(root)
    btns.pack(fill="x", **pad)
    for label, cmd in [("Open .txt", on_open), ("Speak", on_speak), ("Stop", on_stop),
                       ("Save audio", on_save), ("Clear", on_clear)]:
        ttk.Button(btns, text=label, command=cmd).pack(side="left", expand=True, fill="x", padx=3)

    root.mainloop()


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def run_cli(args):
    tts = TTSConverter()

    if args.list_voices:
        for vid, name in TTSConverter.list_voices():
            print(f"{name}\n    id: {vid}")
        return

    if args.file:
        with open(args.file, "r", encoding="utf-8", errors="replace") as f:
            text = f.read().strip()
    else:
        text = (args.text or "").strip()

    if not text:
        sys.exit("No text provided. Use --text or --file.")

    if args.engine == "offline":
        if args.out:
            tts.save_offline(text, args.out, args.rate, args.volume, args.voice)
            print(f"Saved to {args.out}")
        else:
            tts.speak_offline(text, args.rate, args.volume, args.voice)
    else:
        if args.out:
            tts.save_online(text, args.out, args.lang, args.slow)
            print(f"Saved to {args.out}")
        else:
            tts.speak_online(text, args.lang, args.slow)


def main():
    p = argparse.ArgumentParser(description="Text-to-Speech Converter")
    p.add_argument("--text", help="Text to speak")
    p.add_argument("--file", help="Path to a .txt file to read")
    p.add_argument("--engine", choices=["offline", "online"], default="offline")
    p.add_argument("--out", help="Save audio to this path instead of playing")
    p.add_argument("--rate", type=int, default=170, help="Speech rate, offline only (default 170)")
    p.add_argument("--volume", type=float, default=1.0, help="Volume 0.0-1.0, offline only")
    p.add_argument("--voice", help="Voice id, offline only (see --list-voices)")
    p.add_argument("--lang", default="en", help="Language code, online only (e.g. en, ta, hi)")
    p.add_argument("--slow", action="store_true", help="Slow speech, online only")
    p.add_argument("--list-voices", action="store_true", help="List offline voices")
    p.add_argument("--gui", action="store_true", help="Launch the GUI")
    args = p.parse_args()

    if args.gui or len(sys.argv) == 1:
        run_gui()
    else:
        try:
            run_cli(args)
        except Exception as e:
            sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
