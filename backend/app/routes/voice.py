
from pathlib import Path
import asyncio
import tempfile
import threading
from io import BytesIO

import av
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gtts import gTTS
from faster_whisper import WhisperModel

router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])

MODEL_SIZE = "tiny"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_DURATION = 30  # seconds

_model = None
_model_lock = threading.Lock()
_transcription_lock = threading.Lock()


def get_model():
    global _model

    if _model is None:
        with _model_lock:
            if _model is None:
                print("VOICE: Loading Whisper tiny model...", flush=True)
                _model = WhisperModel(
                    MODEL_SIZE,
                    device="cpu",
                    compute_type="int8",
                    cpu_threads=2,
                    num_workers=1,
                )
                print("VOICE: Whisper model loaded.", flush=True)

    return _model


def decode_audio(file_path: str):
    chunks = []

    with av.open(file_path) as container:
        audio_stream = next(
            (s for s in container.streams if s.type == "audio"),
            None,
        )

        if audio_stream is None:
            raise ValueError("No audio stream found.")

        resampler = av.audio.resampler.AudioResampler(
            format="s16",
            layout="mono",
            rate=16000,
        )

        for frame in container.decode(audio_stream):
            frames = resampler.resample(frame)
            if not isinstance(frames, list):
                frames = [frames]

            for item in frames:
                if item is not None:
                    chunks.append(item.to_ndarray().reshape(-1))

        remaining = resampler.resample(None)
        if not isinstance(remaining, list):
            remaining = [remaining]

        for item in remaining:
            if item is not None:
                chunks.append(item.to_ndarray().reshape(-1))

    if not chunks:
        raise ValueError("No audio samples found.")

    audio = np.concatenate(chunks).astype(np.float32) / 32768.0

    duration = len(audio) / 16000
    if duration > MAX_DURATION:
        raise ValueError(
            f"Recording is too long ({duration:.1f}s). "
            f"Please record no more than {MAX_DURATION} seconds."
        )

    return audio


def transcribe_audio(audio):
    # Serialize inference to reduce CPU and memory pressure.
    with _transcription_lock:
        model = get_model()

        segments, info = model.transcribe(
            audio,
            task="transcribe",
            beam_size=1,
            best_of=1,
            temperature=0,
            vad_filter=True,
            without_timestamps=True,
            condition_on_previous_text=False,
        )

        parts = []
        for segment in segments:
            text = segment.text.strip()
            if text:
                parts.append(text)

        transcript = " ".join(parts).strip()
        detected_language = info.language or "unknown"
        probability = float(info.language_probability or 0)

    return transcript, detected_language, probability


@router.post("/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
    filename = file.filename or "voice.webm"
    suffix = Path(filename).suffix.lower()

    supported_extensions = {
        ".webm", ".wav", ".mp3", ".m4a", ".ogg", ".mp4"
    }

    content_type = (file.content_type or "").lower()

    if not (
        content_type.startswith("audio/")
        or content_type.startswith("video/")
        or suffix in supported_extensions
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload an audio recording.",
        )

    temp_path = None

    try:
        # Read at most 10 MB plus one byte to detect oversized uploads.
        contents = await file.read(MAX_FILE_SIZE + 1)

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="The audio recording is empty.",
            )

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Recording exceeds 10 MB. Please record a shorter clip.",
            )

        suffix = suffix if suffix in supported_extensions else ".webm"

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        print(
            f"VOICE: Request received; file={filename}, "
            f"bytes={len(contents)}",
            flush=True,
        )

        # Decode outside the async event loop.
        audio = await asyncio.to_thread(decode_audio, temp_path)

        duration = len(audio) / 16000
        rms = float(np.sqrt(np.mean(np.square(audio))))
        peak = float(np.max(np.abs(audio)))

        print(
            f"VOICE: Audio decoded; duration={duration:.2f}s, "
            f"rms={rms:.6f}, peak={peak:.6f}",
            flush=True,
        )

        if duration < 0.8:
            raise HTTPException(
                status_code=400,
                detail="Recording is too short. Please speak for at least 2 seconds.",
            )

        if rms < 0.003 or peak < 0.02:
            raise HTTPException(
                status_code=400,
                detail="Very little sound detected. Check your microphone and try again.",
            )

        print("VOICE: Starting transcription.", flush=True)

        transcript, detected_language, probability = await asyncio.to_thread(
            transcribe_audio, audio
        )

        print(
            f"VOICE: Finished; language={detected_language}, "
            f"probability={probability:.4f}, "
            f"transcript_length={len(transcript)}",
            flush=True,
        )

        if not transcript:
            raise HTTPException(
                status_code=400,
                detail="No clear speech detected. Please try again.",
            )

        final_language = "te" if detected_language == "te" else "en"
        language_name = "Telugu" if final_language == "te" else "English"

        return {
            "success": True,
            "transcript": transcript,
            "detected_language": final_language,
            "language_name": language_name,
            "response_language": final_language,
            "language_probability": round(probability, 4),
            "audio_duration": round(duration, 2),
            "audio_rms": round(rms, 6),
            "audio_peak": round(peak, 6),
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(
            f"VOICE ERROR: {type(exc).__name__}: {exc}",
            flush=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Voice transcription failed. Please try a shorter recording.",
        )

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception as exc:
                print(f"VOICE: Temp cleanup warning: {exc}", flush=True)

        await file.close()


class SpeakRequest(BaseModel):
    text: str
    language: str = "te"


def _make_speech_response(text: str, language: str):
    clean_text = (text or "").strip()
    clean_language = (language or "te").strip().lower()

    if not clean_text:
        raise HTTPException(status_code=400, detail="Text is required.")

    if clean_language not in {"te", "en"}:
        raise HTTPException(
            status_code=400,
            detail="Supported languages are Telugu and English.",
        )

    try:
        audio_buffer = BytesIO()
        gTTS(
            text=clean_text,
            lang=clean_language,
            slow=False,
        ).write_to_fp(audio_buffer)

        audio_buffer.seek(0)
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
        )

    except Exception as exc:
        print(f"TEXT-TO-SPEECH ERROR: {exc}", flush=True)
        raise HTTPException(
            status_code=502,
            detail="Could not generate speech. Check the speech service connection.",
        )


@router.post("/speak")
async def speak_text(data: SpeakRequest):
    return await asyncio.to_thread(
        _make_speech_response, data.text, data.language
    )


@router.get("/speak")
async def speak_text_get(text: str, language: str = "te"):
    return await asyncio.to_thread(
        _make_speech_response, text, language
    )
