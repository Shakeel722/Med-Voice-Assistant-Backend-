import os
from pydub import AudioSegment

# Try to import Coqui TTS; if unavailable, fallback to pyttsx3
try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except Exception:
    COQUI_AVAILABLE = False


def synthesize_text_to_wav_bytes(text: str, voice: str = None):
    tmp_wav = 'temp_tts.wav'
    tmp_mp3 = 'temp_tts.mp3'

    if COQUI_AVAILABLE:
        MODEL_NAME = os.getenv('TTS_MODEL', 'tts_models/en/ljspeech/tacotron2-DDC')
        tts = TTS(MODEL_NAME, progress_bar=False, gpu=False)
        if voice:
            tts.tts_to_file(text=text, speaker=voice, file_path=tmp_wav)
        else:
            tts.tts_to_file(text=text, file_path=tmp_wav)
    else:
        # fallback to pyttsx3
        try:
            import pyttsx3
        except Exception as e:
            raise RuntimeError('No TTS backend available: install TTS or pyttsx3') from e

        engine = pyttsx3.init()
        engine.save_to_file(text, tmp_wav)
        engine.runAndWait()

    # Return raw WAV bytes (avoids requiring ffmpeg for mp3 conversion)
    with open(tmp_wav, 'rb') as f:
        data = f.read()
    # cleanup optional
    try:
        os.remove(tmp_wav)
        os.remove(tmp_mp3)
    except Exception:
        pass
    return data
