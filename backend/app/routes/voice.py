from pathlib import Path
import tempfile
from io import BytesIO

import av
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gtts import gTTS
from faster_whisper import WhisperModel

router = APIRouter(
    prefix="/api/voice",
    tags=["Voice Assistant"]
)

MODEL_SIZE = "large-v3"

_model = None


def get_model():
    global _model

    if _model is None:
        _model = WhisperModel(
            MODEL_SIZE,
            device="cpu",
            compute_type="int8"
        )

    return _model


def decode_audio(file_path: str):
    container = av.open(file_path)

    audio_stream = None

    for stream in container.streams:
        if stream.type == "audio":
            audio_stream = stream
            break

    if audio_stream is None:
        container.close()
        raise ValueError("No audio stream found.")

    resampler = av.audio.resampler.AudioResampler(
        format="s16",
        layout="mono",
        rate=16000
    )

    chunks = []

    for frame in container.decode(audio_stream):
        resampled_frames = resampler.resample(frame)

        if not isinstance(resampled_frames, list):
            resampled_frames = [resampled_frames]

        for resampled in resampled_frames:
            array = resampled.to_ndarray()

            if array.ndim == 2:
                array = array[0]

            chunks.append(array)

    container.close()

    if not chunks:
        raise ValueError("No audio samples found.")

    audio = np.concatenate(chunks).astype(
        np.float32
    )

    audio /= 32768.0

    return audio


def get_audio_stats(audio):
    duration = len(audio) / 16000

    rms = float(
        np.sqrt(
            np.mean(
                np.square(audio)
            )
        )
    )

    peak = float(
        np.max(
            np.abs(audio)
        )
    )

    return duration, rms, peak


def transcribe_audio(
    model,
    audio,
    language=None
):
    segments, info = model.transcribe(
        audio,
        language=language,
        task="transcribe",
        beam_size=5,
        best_of=5,
        temperature=0,
        vad_filter=True,
        without_timestamps=True,
        condition_on_previous_text=False
    )

    parts = []

    for segment in segments:
        text = segment.text.strip()

        if text:
            parts.append(text)

    transcript = " ".join(parts).strip()

    return transcript, info


@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...)
):
    if not file.content_type:
        raise HTTPException(
            status_code=400,
            detail="Audio file is required."
        )

    if not (
        file.content_type.startswith("audio/")
        or file.content_type.startswith("video/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload an audio recording."
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The audio recording is empty."
        )

    suffix = (
        Path(
            file.filename or "voice.webm"
        ).suffix
        or ".webm"
    )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        # ------------------------------------------------
        # Decode browser WebM/Opus audio ourselves
        # ------------------------------------------------
        audio = decode_audio(temp_path)

        duration, rms, peak = get_audio_stats(
            audio
        )

        print("\n========== AUDIO DEBUG ==========")
        print("Duration:", round(duration, 2), "seconds")
        print("RMS:", rms)
        print("Peak:", peak)
        print("File:", file.filename)
        print("Content type:", file.content_type)
        print("=================================\n")

        # ------------------------------------------------
        # Reject silent / almost silent recordings
        # ------------------------------------------------
        if duration < 0.8:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Recording is too short. "
                    "Please speak for at least 2 seconds."
                )
            )

        if rms < 0.003 or peak < 0.02:
            raise HTTPException(
                status_code=400,
                detail=(
                    "The recording contains very little "
                    "audible sound. Please check your "
                    "microphone and speak closer to it."
                )
            )

        model = get_model()

        # ------------------------------------------------
        # First pass: automatic language detection
        # ------------------------------------------------
        detect_segments, detect_info = model.transcribe(
            audio,
            language=None,
            task="transcribe",
            beam_size=5,
            temperature=0,
            vad_filter=True,
            without_timestamps=True,
            condition_on_previous_text=False
        )

        detected_language = (
            detect_info.language or "unknown"
        )

        language_probability = float(
            detect_info.language_probability or 0
        )

        print(
            "Detected language:",
            detected_language
        )

        print(
            "Language probability:",
            language_probability
        )

        # ------------------------------------------------
        # Short/uncertain recordings:
        # explicitly test Telugu and English.
        # ------------------------------------------------
        if (
            detected_language == "te"
            and language_probability >= 0.75
        ):
            final_language = "te"

            transcript, _ = transcribe_audio(
                model,
                audio,
                language="te"
            )

        elif (
            detected_language == "en"
            and language_probability >= 0.90
        ):
            final_language = "en"

            transcript, _ = transcribe_audio(
                model,
                audio,
                language="en"
            )

        else:
            telugu_transcript, _ = (
                transcribe_audio(
                    model,
                    audio,
                    language="te"
                )
            )

            english_transcript, _ = (
                transcribe_audio(
                    model,
                    audio,
                    language="en"
                )
            )

            print(
                "Telugu candidate:",
                telugu_transcript
            )

            print(
                "English candidate:",
                english_transcript
            )

            telugu_chars = sum(
                1
                for char in telugu_transcript
                if "\u0C00" <= char <= "\u0C7F"
            )

            english_chars = sum(
                1
                for char in english_transcript
                if char.isascii()
                and char.isalpha()
            )

            # Strong Telugu-script evidence
            if telugu_chars >= 2:
                final_language = "te"
                transcript = telugu_transcript

            elif (
                detected_language == "en"
                and language_probability >= 0.75
                and english_chars >= 5
            ):
                final_language = "en"
                transcript = english_transcript
               

            elif detected_language == "te":
                final_language = "te"
                transcript = telugu_transcript

            else:
                final_language = "en"
                transcript = english_transcript

        transcript = transcript.strip()

        if not transcript:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No clear speech was detected. "
                    "Please speak again."
                )
            )

        # ------------------------------------------------
        # Reject obvious Whisper hallucination
        # ------------------------------------------------
        if final_language == "te":
            language_name = "Telugu"
            response_language = "te"

        else:
            language_name = "English"
            response_language = "en"

        return {
            "success": True,
            "transcript": transcript,
            "detected_language": final_language,
            "language_name": language_name,
            "response_language": response_language,
            "language_probability": round(
                language_probability,
                4
            ),
            "audio_duration": round(
                duration,
                2
            ),
            "audio_rms": round(
                rms,
                6
            ),
            "audio_peak": round(
                peak,
                6
            )
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(
            "VOICE TRANSCRIPTION ERROR:",
            repr(exc)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Voice transcription failed."
            )
        )

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(
                    missing_ok=True
                )
            except Exception:
                pass

# Text-to-speech request model. POST is used so long Telugu answers are not
# placed in the URL, which can exceed browser/server URL length limits.
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
        gTTS(text=clean_text, lang=clean_language, slow=False).write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return StreamingResponse(audio_buffer, media_type="audio/mpeg")
    except Exception as exc:
        print("TEXT-TO-SPEECH ERROR:", repr(exc))
        raise HTTPException(
            status_code=502,
            detail="Could not generate speech. Check your internet connection.",
        )


@router.post("/speak")
async def speak_text(data: SpeakRequest):
    return _make_speech_response(data.text, data.language)


# Keep the GET endpoint too, so the short browser test URL used earlier still works.
@router.get("/speak")
async def speak_text_get(text: str, language: str = "te"):
    return _make_speech_response(text, language)
