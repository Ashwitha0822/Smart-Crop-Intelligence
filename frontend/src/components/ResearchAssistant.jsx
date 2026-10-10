import React, { useState } from "react";

const API = "https://smart-crop-intelligence.onrender.com";

function ResearchAssistant({ language = "en" }) {
  const isTelugu = language === "te";

  const [crop, setCrop] = useState("Rice");
  const [topic, setTopic] = useState(
    "Crop Health"
  );
  const [question, setQuestion] =
    useState("");

  const [answer, setAnswer] =
    useState("");

  const [sources, setSources] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const text = {
    title: isTelugu
      ? "🤖 AI పంట పరిశోధన"
      : "🤖 AI Crop Research",

    subtitle: isTelugu
      ? "వ్యవసాయం, పంట ఆరోగ్యం, వ్యాధులు, పురుగులు మరియు ఇతర అంశాలపై తాజా సమాచారాన్ని పరిశోధించండి."
      : "Research current information about crops, crop health, diseases, pests and other agricultural topics.",

    crop: isTelugu
      ? "పంట"
      : "Crop",

    topic: isTelugu
      ? "అంశం"
      : "Topic",

    question: isTelugu
      ? "మీ ప్రశ్న"
      : "Your Question",

    questionPlaceholder: isTelugu
      ? "ఉదా: వరి పంటలో NDVI ఎందుకు తగ్గుతుంది?"
      : "Example: Why is NDVI low in rice?",

    research: isTelugu
      ? "🔍 పరిశోధించండి"
      : "🔍 Research",

    researching: isTelugu
      ? "పరిశోధిస్తోంది..."
      : "Researching...",

    answer: isTelugu
      ? "📚 AI పరిశోధన ఫలితం"
      : "📚 AI Research Answer",

    sources: isTelugu
      ? "🌐 మూలాలు"
      : "🌐 Sources",

    noQuestion: isTelugu
      ? "దయచేసి ఒక ప్రశ్నను నమోదు చేయండి."
      : "Please enter a question.",

    error: isTelugu
      ? "పరిశోధన విఫలమైంది."
      : "Research failed.",

    sourceOpen: isTelugu
      ? "మూలాన్ని తెరవండి"
      : "Open Source",

    note: isTelugu
      ? "గమనిక: AI ఇచ్చే సమాచారం సహాయక పరిశోధన సమాచారం మాత్రమే. తుది వ్యవసాయ నిర్ణయాలకు స్థానిక వ్యవసాయ నిపుణుల సలహాను ఉపయోగించండి."
      : "Note: AI-generated information is for research assistance. Use local agricultural guidance for final farming decisions.",
  };

  const research = async () => {
    if (!question.trim()) {
      setError(text.noQuestion);
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(
        `${API_BASE}/api/research`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            question:
              question.trim(),
            crop,
            topic,
            language,
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || text.error
        );
      }

      setAnswer(
        data.answer || ""
      );

      setSources(
        Array.isArray(data.sources)
          ? data.sources
          : []
      );
    } catch (err) {
      console.error(
        "RESEARCH ERROR:",
        err
      );

      setError(
        err.message || text.error
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>{text.title}</h2>

      <p>{text.subtitle}</p>

      <div className="panel">

        {/* CROP */}

        <label>
  {text.crop}

  <select
    value={crop}
    onChange={(e) =>
      setCrop(e.target.value)
    }
  >
    <option value="Rice">
      {language === "te" ? "వరి" : "Rice"}
    </option>

    <option value="Maize">
      {language === "te" ? "మొక్కజొన్న" : "Maize"}
    </option>

    <option value="Apple">
      {language === "te" ? "ఆపిల్" : "Apple"}
    </option>

    <option value="Banana">
      {language === "te" ? "అరటి" : "Banana"}
    </option>

    <option value="Chickpea">
      {language === "te" ? "శనగ" : "Chickpea"}
    </option>

    <option value="Cotton">
      {language === "te" ? "పత్తి" : "Cotton"}
    </option>

    <option value="Grape">
      {language === "te" ? "ద్రాక్ష" : "Grape"}
    </option>

    <option value="Mango">
      {language === "te" ? "మామిడి" : "Mango"}
    </option>

    <option value="Orange">
      {language === "te" ? "నారింజ" : "Orange"}
    </option>

    <option value="Papaya">
      {language === "te" ? "బొప్పాయి" : "Papaya"}
    </option>

    <option value="Pomegranate">
      {language === "te" ? "దానిమ్మ" : "Pomegranate"}
    </option>

    <option value="Watermelon">
      {language === "te" ? "పుచ్చకాయ" : "Watermelon"}
    </option>
  </select>
</label>

        {/* TOPIC */}

        <label
  style={{
    marginTop: "15px",
  }}
>
  {text.topic}

  <select
    value={topic}
    onChange={(e) =>
      setTopic(e.target.value)
    }
  >
    <option value="Crop Health">
      {language === "te" ? "పంట ఆరోగ్యం" : "Crop Health"}
    </option>

    <option value="Disease">
      {language === "te" ? "వ్యాధి" : "Disease"}
    </option>

    <option value="Pest">
      {language === "te" ? "పురుగు" : "Pest"}
    </option>

    <option value="Weather">
      {language === "te" ? "వాతావరణం" : "Weather"}
    </option>

    <option value="Soil">
      {language === "te" ? "నేల" : "Soil"}
    </option>

    <option value="Farming Practices">
      {language === "te" ? "వ్యవసాయ పద్ధతులు" : "Farming Practices"}
    </option>

    <option value="General Agriculture">
      {language === "te" ? "సాధారణ వ్యవసాయం" : "General Agriculture"}
    </option>
  </select>
</label>

        {/* QUESTION */}

        <label
          style={{
            marginTop: "15px",
          }}
        >
          {text.question}

          <textarea
            rows={5}
            value={question}
            placeholder={
              text.questionPlaceholder
            }
            onChange={(e) =>
              setQuestion(
                e.target.value
              )
            }
            style={{
              width: "100%",
              marginTop: "8px",
              padding: "12px",
              borderRadius: "8px",
              border:
                "1px solid #ccc",
              resize: "vertical",
              fontFamily:
                "inherit",
              fontSize: "15px",
            }}
          />
        </label>

        {/* BUTTON */}

        <button
          className="primary"
          onClick={research}
          disabled={loading}
          style={{
            marginTop: "16px",
          }}
        >
          {loading
            ? text.researching
            : text.research}
        </button>
      </div>

      {/* ERROR */}

      {error && (
        <div
          className="error-message"
          style={{
            marginTop: "16px",
          }}
        >
          {error}
        </div>
      )}

      {/* ANSWER */}

      {answer && (
        <div
          className="result"
          style={{
            marginTop: "24px",
          }}
        >
          <h2>{text.answer}</h2>

          <div
            style={{
              whiteSpace:
                "pre-wrap",
              lineHeight: "1.7",
            }}
          >
            {answer}
          </div>
        </div>
      )}

      {/* SOURCES */}

      {sources.length > 0 && (
        <div
          className="panel"
          style={{
            marginTop: "24px",
          }}
        >
          <h2>{text.sources}</h2>

          {sources.map(
            (source, index) => (
              <div
                key={
                  source.url ||
                  index
                }
                style={{
                  padding:
                    "14px 0",
                  borderBottom:
                    "1px solid rgba(128,128,128,0.2)",
                }}
              >
                <strong>
                  {source.title}
                </strong>

                {source.snippet && (
                  <p
                    style={{
                      margin:
                        "8px 0",
                      opacity: 0.8,
                    }}
                  >
                    {source.snippet}
                  </p>
                )}

                <a
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  {text.sourceOpen}
                </a>
              </div>
            )
          )}
        </div>
      )}

      <p
        style={{
          marginTop: "20px",
          fontSize: "13px",
          opacity: 0.75,
        }}
      >
        {text.note}
      </p>
    </section>
  );
}

export default ResearchAssistant;