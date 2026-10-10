import React, { useEffect, useRef, useState } from "react";
import { translations } from "../i18n/translations";

const API_BASE = "https://smart-crop-intelligence.onrender.com";

const normalizeSpeechLanguage = (value) => {
  const normalized = String(value || "").trim().toLowerCase();
  return normalized === "te" || normalized.startsWith("te-") || normalized.includes("telugu")
    ? "te"
    : "en";
};

export default function VoiceAssistant({language}) {
  const text = translations[language] || translations.en;
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [detectedLanguage, setDetectedLanguage] = useState("");
  const [responseLanguage, setResponseLanguage] = useState("en");
  const [speechPreparing, setSpeechPreparing] = useState(false);
  const [speechReady, setSpeechReady] = useState(false);
  const [languageProbability, setLanguageProbability] = useState(0);
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [error, setError] = useState("");


  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const audioRef = useRef(null);
  const audioUrlRef = useRef(null);
  const speechBlobRef = useRef(null);

  // Stop audio and release its temporary URL when this component unmounts.
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
        audioUrlRef.current = null;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    setError("");
    setTranscript("");
    setAnswer("");
    setSources([]);
    setDetectedLanguage("");
    setResponseLanguage("en");
    setLanguageProbability(0);
    setSpeechReady(false);
    setSpeechPreparing(false);
    speechBlobRef.current = null;
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = null;
    }

    try {
      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

      streamRef.current = stream;

      const recorder = new MediaRecorder(stream);

      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type: "audio/webm",
          }
        );

        stream.getTracks().forEach((track) =>
          track.stop()
        );

        streamRef.current = null;

        await processVoice(audioBlob);
      };

      recorder.start();

      setIsRecording(true);
    } catch (err) {
      console.error(err);

      setError(
        "Microphone access failed. Please allow microphone permission."
      );
    }
  };

  const stopRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
    }

    setIsRecording(false);
  };

  const processVoice = async (audioBlob) => {
    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);
    setSpeechReady(false);
    setSpeechPreparing(false);
    speechBlobRef.current = null;

    try {
      const formData = new FormData();
      formData.append("file", audioBlob, "farmer_voice.webm");

      const voiceResponse = await fetch(`${API_BASE}/api/voice/transcribe`, {
        method: "POST",
        body: formData,
      });
      
      const responseText = await voiceResponse.text();

let voiceData = {};
try {
  voiceData = responseText ? JSON.parse(responseText) : {};
} catch {
  voiceData = {};
}

if (!voiceResponse.ok) {
  throw new Error(
    voiceData.detail ||
    `Voice transcription failed (HTTP ${voiceResponse.status}). ` +
    (responseText || "The server returned an empty error response.")
  );
}
      

      console.log("VOICE RESULT:", voiceData);
      setTranscript(voiceData.transcript || "");
      setDetectedLanguage(voiceData.language_name || "Unknown");
      setLanguageProbability(voiceData.language_probability || 0);

      const detectedResponseLanguage = normalizeSpeechLanguage(
        voiceData.response_language || voiceData.detected_language || voiceData.language_name
      );
      setResponseLanguage(detectedResponseLanguage);

      // Automatically search for an answer as soon as transcription finishes.
      // Pass the new values directly because React state updates are asynchronous.
      await getAnswer(voiceData.transcript || "", detectedResponseLanguage);
    } catch (err) {
      console.error("Voice transcription error:", err);
      setError(err.message || "Something went wrong while transcribing your voice.");
    } finally {
      setLoading(false);
    }
  };

  const getAnswer = async (questionText = transcript, languageToUse = responseLanguage) => {
    const question = String(questionText || "").trim();
    if (!question) {
      setError("Please enter or correct your question first.");
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);
    setSpeechReady(false);
    setSpeechPreparing(false);
    speechBlobRef.current = null;

    try {
      const researchResponse = await fetch(`${API_BASE}/api/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          crop: "General Agriculture",
          topic: "Agriculture",
          language: languageToUse,
        }),
      });
      const researchData = await researchResponse.json();

      if (!researchResponse.ok) {
        throw new Error(researchData.detail || "Research request failed.");
      }

      const answerText = (researchData.answer || "").trim();
      setAnswer(answerText);
      setSources(researchData.sources || []);

      if (!answerText) {
        throw new Error("The research service returned an empty answer.");
      }

      // Prepare the audio before the user presses Speak Answer. This avoids
      // browser autoplay restrictions after waiting for a network request.
      setSpeechPreparing(true);
      const speechResponse = await fetch(`${API_BASE}/api/voice/speak`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: answerText, language: languageToUse }),
      });

      if (!speechResponse.ok) {
        let message = "Unable to prepare speech audio.";
        try {
          const errorData = await speechResponse.json();
          message = errorData.detail || message;
        } catch {
          // Keep the default message if the server did not return JSON.
        }
        throw new Error(message);
      }

      const speechBlob = await speechResponse.blob();
      if (!speechBlob.size) {
        throw new Error("The speech service returned an empty audio file.");
      }
      speechBlobRef.current = speechBlob;
      setSpeechReady(true);
    } catch (err) {
      console.error("Research/audio preparation error:", err);
      setError(err.message || "Could not prepare the answer or its audio.");
    } finally {
      setLoading(false);
      setSpeechPreparing(false);
    }
  };

  const speakAnswer = async () => {
    const speechBlob = speechBlobRef.current;
    if (!speechBlob) {
      setError("Audio is not ready yet. Please wait for audio preparation to finish and try again.");
      return;
    }

    setError("");
    try {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        audioRef.current = null;
      }
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
        audioUrlRef.current = null;
      }

      const audioUrl = URL.createObjectURL(speechBlob);
      audioUrlRef.current = audioUrl;
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onplay = () => setSpeaking(true);
      audio.onended = () => {
        setSpeaking(false);
        if (audioRef.current === audio) audioRef.current = null;
        if (audioUrlRef.current === audioUrl) {
          URL.revokeObjectURL(audioUrl);
          audioUrlRef.current = null;
        }
      };
      audio.onerror = () => {
        setSpeaking(false);
        setError("The audio file was prepared, but the browser could not play it. Check your sound output and try again.");
        if (audioRef.current === audio) audioRef.current = null;
        if (audioUrlRef.current === audioUrl) {
          URL.revokeObjectURL(audioUrl);
          audioUrlRef.current = null;
        }
      };

      // This call is made directly from the user's button click using cached
      // audio, with no network wait in between.
      await audio.play();
    } catch (err) {
      console.error("Audio playback error:", err);
      setSpeaking(false);
      setError(err.message || "Unable to play the answer audio. Check your device volume.");
    }
  };

  const stopVoice = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = null;
    }
    setSpeaking(false);
  };

  return (
    <div className="page-card">

      <div className="page-header">
        <h2>🎙️ {text.voiceTitle}</h2>
        <p>{text.voiceDescription}</p>
      </div>

      <div className="voice-card">

        <div className="voice-buttons">

          {!isRecording ? (
            <button
              className="primary-button"
              onClick={startRecording}
              disabled={loading}
            >
               🎤 {isRecording ? text.stopSpeaking : text.startSpeaking}
              
            </button>
          ) : (
            <button
              className="danger-button"
              onClick={stopRecording}
            >
              ⏹ Stop Recording
            </button>
          )}

          {speaking && (
            <button
              className="secondary-button"
              onClick={stopVoice}
            >
              🔇 Stop Voice
            </button>
          )}

        </div>

        {isRecording && (
          <div className="recording-status">
            🔴 Listening... Speak clearly.
          </div>
        )}

        {loading && (
          <div className="loading-text">
            ⏳ Detecting language and preparing
            your answer...
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {detectedLanguage && (
          <div className="language-result">

            <strong>
              Detected Language:
            </strong>{" "}
            {detectedLanguage}

            <br />

            <strong>
              Detection Confidence:
            </strong>{" "}
            {(languageProbability * 100).toFixed(1)}%

          </div>
        )}

        {transcript && (
          <div className="result-section">
            <h3>🗣️ Farmer Question</h3>
            <div className="result-box">{transcript}</div>
          </div>
        )}

        {answer && (
          <div className="result-section">

            <h3>🤖 AI Answer</h3>

            <div className="result-box">
              {answer}
            </div>

            <button
              className="secondary-button"
              onClick={speakAnswer}
              disabled={!speechReady || speechPreparing}
            >
              {speechPreparing ? "Preparing audio..." : "🔊 Speak Answer / సమాధానం వినండి"}
            </button>

          </div>
        )}

        {sources.length > 0 && (
          <div className="result-section">

            <h3>📚 Sources</h3>

            <div className="source-list">

              {sources.map(
                (source, index) => (
                  <div
                    className="source-item"
                    key={index}
                  >
                    <strong>
                      {source.title ||
                        "Source"}
                    </strong>

                    {source.url && (
                      <div>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          View Source
                        </a>
                      </div>
                    )}
                  </div>
                )
              )}

            </div>

          </div>
        )}

      </div>

    </div>
  );
}