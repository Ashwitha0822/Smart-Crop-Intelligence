
import asyncio
import os
from io import BytesIO
from pathlib import Path

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gtts import gTTS

router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
SARVAM_URL = "https://api.sarvam.ai/speech-to-text"
SUPPORTED_EXTENSIONS = {
    ".webm", ".wav", ".mp3", ".m4a", ".ogg", ".mp4",
    ".aac", ".flac", ".opus", ".aiff", ".amr", ".wma",
}


def transcribe_with_sarvam(
    contents: bytes,
    filename: str,
    content_type: str,
):
    api_key = os.getenv("SARVAM_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Speech recognition is not configured on the server.",
        )

    headers = {"api-subscription-key": api_key}
    files = {
        "file": (
            filename,
            contents,
            content_type or "application/octet-stream",
        )
    }
    data = {
        "model": "saaras:v4",
        "language_code": "unknown",
    }

    try:
        response = httpx.post(
            SARVAM_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=45.0,
        )

        if response.status_code in (401, 403):
            print(
                f"SARVAM AUTH ERROR: HTTP {response.status_code}",
                flush=True,
            )
            raise HTTPException(
                status_code=502,
                detail="Speech recognition API authentication failed. Check the server API key.",
            )

        if response.status_code == 429:
            raise HTTPException(
                status_code=503,
                detail="Speech recognition is busy. Please try again shortly.",
            )

        if response.status_code >= 400:
            print(
                f"SARVAM API ERROR: HTTP {response.status_code}: "
                f"{response.text[:500]}",
                flush=True,
            )
            raise HTTPException(
                status_code=502,
                detail="The speech recognition service could not process this recording.",
            )

        result = response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Speech recognition took too long. Please try a shorter recording.",
        )
    except httpx.RequestError as exc:
        print(f"SARVAM CONNECTION ERROR: {exc}", flush=True)
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the speech recognition service.",
        )

    transcript = (result.get("transcript") or "").strip()
    language_code = (result.get("language_code") or "").lower()

    if language_code.startswith("te"):
        detected_language = "te"
    elif language_code.startswith("en"):
        detected_language = "en"
    else:
        # Preserve the transcript even if the provider cannot identify
        # the language. The app supports Telugu and English responses.
        detected_language = "te" if any(
            "\u0c00" <= char <= "\u0c7f" for char in transcript
        ) else "en"

    probability = result.get("language_probability")
    try:
        probability = float(probability) if probability is not None else 0.0
    except (TypeError, ValueError):
        probability = 0.0

    return transcript, detected_language, probability


@router.post("/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
    filename = Path(file.filename or "voice.webm").name
    suffix = Path(filename).suffix.lower()
    content_type = (file.content_type or "").lower()

    if not (
        content_type.startswith("audio/")
        or content_type.startswith("video/")
        or suffix in SUPPORTED_EXTENSIONS
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload an audio recording.",
        )

    try:
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

        print(
            f"VOICE: Sending audio to hosted transcription; "
            f"file={filename}, bytes={len(contents)}",
            flush=True,
        )

        transcript, detected_language, probability = await asyncio.to_thread(
            transcribe_with_sarvam,
            contents,
            filename,
            content_type,
        )

        print(
            f"VOICE: Transcription finished; language={detected_language}, "
            f"transcript_length={len(transcript)}",
            flush=True,
        )

        if not transcript:
            raise HTTPException(
                status_code=400,
                detail="No clear speech detected. Please try again.",
            )

        language_name = "Telugu" if detected_language == "te" else "English"

        return {
            "success": True,
            "transcript": transcript,
            "detected_language": detected_language,
            "language_name": language_name,
            "response_language": detected_language,
            "language_probability": round(probability, 4),
            # These are null because audio is no longer decoded locally.
            "audio_duration": None,
            "audio_rms": None,
            "audio_peak": None,
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
            detail="Voice transcription failed. Please try again.",
        )
    finally:
        await file.close()


class SpeakRequest(BaseModel):
    text: str
    language: str = "te"


def _make_speech_response(text: str, language: str):
    clean_text = (text or "").strip()
    clean_language = (language or "te").strip().lower()

    if not clean_text:
        raise HTTPException(
            status_code=400,
            detail="Text is required.",
        )

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
