import React, { useState } from "react";

const API_BASE = "https://smart-crop-intelligence.onrender.com";

// Display translations only. The original English class names are still sent to the API.
const PEST_NAMES_TE = {
  "army worm": "సైనిక పురుగు",
  armyworm: "సైనిక పురుగు",
  "fall armyworm": "శరదృతువు సైనిక పురుగు",
  "beet armyworm": "బీట్ సైనిక పురుగు",
  "rice leaf roller": "వరి ఆకులను చుట్టే పురుగు",
  "rice leaf folder": "వరి ఆకు మడత పురుగు",
  "rice leaf folder moth": "వరి ఆకు మడత చిమ్మట",
  "asiatic rice borer": "ఆసియా వరి కాండం తొలిచే పురుగు",
  "yellow rice borer": "పసుపు వరి కాండం తొలిచే పురుగు",
  "rice stem borer": "వరి కాండం తొలిచే పురుగు",
  "stem borer": "కాండం తొలిచే పురుగు",
  "corn borer": "మొక్కజొన్న కాండం తొలిచే పురుగు",
  "maize borer": "మొక్కజొన్న కాండం తొలిచే పురుగు",
  "cotton bollworm": "పత్తి కాయ తొలిచే పురుగు",
  bollworm: "కాయ తొలిచే పురుగు",
  cutworm: "కత్తిరించే పురుగు",
  aphid: "పేను పురుగు",
  aphids: "పేను పురుగులు",
  whitefly: "తెల్లదోమ",
  whiteflies: "తెల్లదోమలు",
  "brown plant hopper": "గోధుమ రంగు వరి దోమ",
  "brown planthopper": "గోధుమ రంగు వరి దోమ",
  "green leafhopper": "ఆకుపచ్చ ఆకు దోమ",
  leafhopper: "ఆకు దోమ",
  thrips: "త్రిప్స్ పురుగులు",
  "red spider mite": "ఎర్ర సాలీడు నల్లి",
  "spider mite": "సాలీడు నల్లి",
  "cotton mealybug": "పత్తి పిండి పురుగు",
  mealybug: "పిండి పురుగు",
  grasshopper: "మిడత",
  locust: "మిడత",
  "rice water weevil": "వరి నీటి వీవిల్ పురుగు",
  "rice gall midge": "వరి గాల్ మిడ్జ్ పురుగు",
  "rice hispa": "వరి హిస్పా పురుగు",
  "rice whorl maggot": "వరి మెలిక ఈగ పురుగు",
  "rice leaf beetle": "వరి ఆకు బీటిల్ పురుగు",
  "slug caterpillar": "స్లగ్ గొంగళి పురుగు",
  jassid: "జాసిడ్ పురుగు",
  "green bug": "ఆకుపచ్చ దోష పురుగు",
  "white grub": "తెల్ల పెంకు పురుగు",
  weevil: "వీవిల్ పురుగు",
  "fruit fly": "పండ్ల ఈగ",
  "diamondback moth": "డైమండ్‌బ్యాక్ చిమ్మట",
};

const CROP_NAMES_TE = {
  rice: "వరి",
  maize: "మొక్కజొన్న",
  corn: "మొక్కజొన్న",
  "corn (maize)": "మొక్కజొన్న",
  apple: "ఆపిల్",
  banana: "అరటి",
  chickpea: "శనగ",
  cotton: "పత్తి",
  grape: "ద్రాక్ష",
  grapes: "ద్రాక్ష",
  mango: "మామిడి",
  orange: "నారింజ",
  papaya: "బొప్పాయి",
  pomegranate: "దానిమ్మ",
  watermelon: "పుచ్చకాయ",
  tomato: "టమాటా",
  potato: "బంగాళాదుంప",
  sugarcane: "చెరకు",
  soybean: "సోయాబీన్",
  groundnut: "వేరుశనగ",
  peanut: "వేరుశనగ",
  chilli: "మిరప",
  chili: "మిరప",
  coconut: "కొబ్బరి",
  paddy: "వరి",
  "rice paddy": "వరి",
  soybean: "సోయాబీన్",
  sorghum: "జొన్న",
  wheat: "గోధుమ",
  barley: "బార్లీ",
  tobacco: "పొగాకు",
};

const GUIDANCE_TEXT_TE = {
  "insect pest": "కీటక పురుగు",
  "larvae feed on rice leaves and can reduce the photosynthetic area.":
    "ఈ పురుగు లార్వాలు వరి ఆకులను తిని, మొక్క కిరణజన్య సంయోగక్రియకు అవసరమైన ఆకు విస్తీర్ణాన్ని తగ్గించవచ్చు.",
  "monitor leaves regularly for folding and larval feeding.":
    "ఆకులు ముడుచుకుపోవడం, లార్వాలు తిన్న ఆనవాళ్లు ఉన్నాయా అని క్రమం తప్పకుండా పరిశీలించండి.",
  "avoid unnecessary excessive nitrogen application.":
    "అవసరం లేకుండా అధిక నత్రజని ఎరువులు వేయవద్దు.",
  "conserve natural enemies and avoid unnecessary broad-spectrum insecticide use.":
    "పురుగులను సహజంగా నియంత్రించే మిత్ర కీటకాలను కాపాడండి. అవసరం లేకుండా విస్తృత ప్రభావం కలిగిన పురుగుమందులను ఉపయోగించవద్దు.",
  "use treatment only when pest pressure reaches the locally recommended threshold.":
    "పురుగు ఉధృతి స్థానికంగా సిఫార్సు చేసిన పరిమితిని దాటినప్పుడే చికిత్స చేపట్టండి.",
  "remove heavily affected plant material where practical.":
    "సాధ్యమైన చోట తీవ్రంగా దెబ్బతిన్న మొక్క భాగాలను తొలగించండి.",
  "use biological or botanical options where locally recommended.":
    "స్థానికంగా సిఫార్సు చేసినప్పుడు జీవ లేదా వృక్ష ఆధారిత నియంత్రణ పద్ధతులను ఉపయోగించండి.",
  "use biological or botanical control options where locally recommended.":
    "స్థానికంగా సిఫార్సు చేసినప్పుడు జీవ లేదా వృక్ష ఆధారిత నియంత్రణ పద్ధతులను ఉపయోగించండి.",
  "if chemical control is necessary, use only a product registered and labelled for the crop and pest in your location.":
    "రసాయన నియంత్రణ అవసరమైతే, మీ ప్రాంతంలో ఆ పంటకు మరియు ఆ పురుగుకు నమోదైన, లేబుల్ సూచనలు ఉన్న ఉత్పత్తినే ఉపయోగించండి.",
  "a caterpillar pest that can rapidly defoliate maize and other crops.":
    "ఈ గొంగళి పురుగు మొక్కజొన్నతో పాటు ఇతర పంటల ఆకులను వేగంగా తినివేసి నష్టం కలిగించవచ్చు.",
  "scout young plants frequently for eggs and caterpillars.":
    "గుడ్లు, గొంగళి పురుగుల కోసం చిన్న మొక్కలను తరచుగా పరిశీలించండి.",
  "remove weeds that can harbour the pest where appropriate.":
    "పురుగులకు ఆశ్రయమివ్వగల కలుపు మొక్కలను అవసరమైన చోట తొలగించండి.",
  "encourage natural enemies.":
    "పురుగులను నియంత్రించే సహజ మిత్ర కీటకాలను కాపాడండి.",
  "take action early when damaging populations are detected.":
    "నష్టం కలిగించే స్థాయిలో పురుగులు కనిపించినప్పుడు ముందుగానే చర్యలు తీసుకోండి.",
  "use biological or botanical control options where locally recommended.":
    "స్థానికంగా సిఫార్సు చేసినప్పుడు జీవ లేదా వృక్ష ఆధారిత నియంత్రణ పద్ధతులను ఉపయోగించండి.",
  "apply pesticide treatment only when needed and according to the registered label.":
    "అవసరమైనప్పుడే పురుగుమందును వాడండి; నమోదైన ఉత్పత్తి లేబుల్‌లోని సూచనలను తప్పనిసరిగా పాటించండి.",
  "rotate approved modes of action where chemical treatment is necessary and recommended.":
    "రసాయన చికిత్స అవసరమని సిఫార్సు చేసినప్పుడు, అనుమతించబడిన భిన్న చర్యా విధానాలున్న మందులను మారుస్తూ ఉపయోగించండి.",
  "use pesticides only when necessary and only products legally registered and labelled for the crop and diagnosed pest in your location. follow the label, protective equipment, application instructions and pre-harvest interval. follow local agricultural recommendations.":
    "పురుగుమందులను అవసరమైనప్పుడే ఉపయోగించండి. మీ ప్రాంతంలో ఆ పంటకు, గుర్తించిన పురుగుకు చట్టబద్ధంగా నమోదైన ఉత్పత్తులనే వాడండి. లేబుల్ సూచనలు, వ్యక్తిగత రక్షణ పరికరాలు, మోతాదు, పిచికారీ విధానం మరియు కోతకు ముందు పాటించాల్సిన వేచి ఉండే వ్యవధిని తప్పనిసరిగా అనుసరించండి. స్థానిక వ్యవసాయ శాఖ సూచనలు పాటించండి.",
  "use biological or botanical control options where locally recommended.":
    "స్థానికంగా సిఫార్సు చేసినప్పుడు జీవ లేదా వృక్ష ఆధారిత నియంత్రణ పద్ధతులను ఉపయోగించండి.",
};

function normalizeText(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[’‘]/g, "'")
    .replace(/\s+/g, " ");
}

function containsTelugu(value) {
  return /[\u0C00-\u0C7F]/.test(String(value ?? ""));
}

function translatePestName(value, language) {
  if (!value || language !== "te" || containsTelugu(value)) return value || "--";
  const key = normalizeText(value).replace(/[_-]+/g, " ");
  return PEST_NAMES_TE[key] || PEST_NAMES_TE[key.replace(/\s+/g, " ")] || "గుర్తించిన పురుగు";
}

function translateCropName(value, language) {
  if (!value || language !== "te" || containsTelugu(value)) return value || "--";
  const key = normalizeText(value).replace(/[_-]+/g, " ");
  return CROP_NAMES_TE[key] || "గుర్తించిన పంట";
}

function translateGuidanceValue(value, kind, language) {
  if (value == null || value === "") return "--";
  if (language !== "te" || containsTelugu(value)) return value;

  const key = normalizeText(value);
  if (GUIDANCE_TEXT_TE[key]) return GUIDANCE_TEXT_TE[key];

  // Never leak an unknown English paragraph into Telugu mode. Use a conservative,
  // clearly general instruction when the backend text has no local translation.
  const fallbacks = {
    type: "కీటక పురుగు",
    summary: "ఈ పురుగు పంటకు నష్టం కలిగించవచ్చు. పంటను క్రమం తప్పకుండా పరిశీలించి, నష్టం కనిపిస్తే స్థానిక వ్యవసాయ నిపుణుల సలహా తీసుకోండి.",
    management: "పంటను తరచుగా పరిశీలించండి. పురుగు ప్రభావం కనిపిస్తే మీ ప్రాంతానికి అనుకూలమైన వ్యవసాయ సిఫార్సుల ప్రకారం చర్యలు తీసుకోండి.",
    treatment: "మీ ప్రాంతంలో ఈ పంటకు, గుర్తించిన పురుగుకు అనుమతించబడిన చికిత్సను మాత్రమే ఉత్పత్తి లేబుల్ సూచనల ప్రకారం ఉపయోగించండి.",
    pesticide_policy: "పురుగుమందులను అవసరమైనప్పుడే ఉపయోగించండి. మీ ప్రాంతంలో ఈ పంటకు, గుర్తించిన పురుగుకు చట్టబద్ధంగా నమోదైన ఉత్పత్తులనే ఉపయోగించండి. లేబుల్ సూచనలు, రక్షణ పరికరాలు, మోతాదు, పిచికారీ విధానం మరియు కోతకు ముందు వేచి ఉండే వ్యవధిని పాటించండి. స్థానిక వ్యవసాయ సిఫార్సులను అనుసరించండి.",
  };
  return fallbacks[kind] || "వివరాలు అందుబాటులో లేవు. స్థానిక వ్యవసాయ నిపుణుల సలహా తీసుకోండి.";
}

function PestDetection({ language = "en" }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [guidance, setGuidance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [guidanceLoading, setGuidanceLoading] = useState(false);
  const [error, setError] = useState("");

  const isTelugu = language === "te";

  const text = {
    title: isTelugu
      ? "🐛 పురుగు గుర్తింపు"
      : "🐛 Pest Detection",

    subtitle: isTelugu
      ? "పురుగు చిత్రాన్ని అప్‌లోడ్ చేసి AI ద్వారా గుర్తించండి."
      : "Upload a pest image to identify it using AI.",

    choose: isTelugu
      ? "📷 పురుగు చిత్రం ఎంచుకోండి"
      : "📷 Choose Pest Image",

    selected: isTelugu
      ? "ఎంచుకున్న చిత్రం"
      : "Selected Image",

    detect: isTelugu
      ? "🔍 పురుగును గుర్తించండి"
      : "🔍 Detect Pest",

    detecting: isTelugu
      ? "గుర్తిస్తోంది..."
      : "Detecting...",

    result: isTelugu
      ? "✅ గుర్తింపు ఫలితం"
      : "✅ Detection Result",

    pest: isTelugu
      ? "పురుగు"
      : "Pest",

    crop: isTelugu
      ? "పంట"
      : "Crop",

    confidence: isTelugu
      ? "నమ్మక స్థాయి"
      : "Confidence",

    top3: isTelugu
      ? "మొదటి 3 అంచనాలు"
      : "Top 3 Predictions",

    guidanceTitle: isTelugu
      ? "🌿 పురుగు నిర్వహణ & చికిత్స మార్గదర్శకం"
      : "🌿 Pest Management & Treatment Guidance",

    pestType: isTelugu
      ? "పురుగు రకం"
      : "Pest Type",

    summary: isTelugu
      ? "సారాంశం"
      : "Summary",

    management: isTelugu
      ? "🌱 నిర్వహణ చర్యలు"
      : "🌱 Management Steps",

    treatment: isTelugu
      ? "🧪 చికిత్స మార్గదర్శకం"
      : "🧪 Treatment Guidance",

    pesticidePolicy: isTelugu
      ? "⚠️ పురుగుమందుల భద్రతా విధానం"
      : "⚠️ Pesticide Safety Policy",

    warning: isTelugu
      ? "⚠️ నమ్మక స్థాయి తక్కువగా ఉంది. దయచేసి పురుగును స్వయంగా ధృవీకరించండి లేదా స్థానిక వ్యవసాయ నిపుణుల సలహా తీసుకోండి."
      : "⚠️ Low confidence prediction. Please verify the pest visually or consult local agricultural guidance.",

    noWarning: isTelugu
      ? "గుర్తింపు నమ్మకం సాపేక్షంగా ఎక్కువగా ఉంది. అయినప్పటికీ వ్యవసాయ నిపుణుల ధృవీకరణ మంచిది."
      : "Prediction confidence is relatively high. Visual or agricultural verification is still recommended.",

    uploadError: isTelugu
      ? "దయచేసి ఒక చిత్రం ఎంచుకోండి."
      : "Please choose an image.",

    invalidImage: isTelugu
      ? "దయచేసి సరైన చిత్ర ఫైల్‌ను ఎంచుకోండి."
      : "Please select a valid image file.",

    serverError: isTelugu
      ? "పురుగు గుర్తించడంలో లోపం ఏర్పడింది."
      : "An error occurred while detecting the pest.",

    guidanceError: isTelugu
      ? "పురుగు నిర్వహణ మార్గదర్శకం లోడ్ కాలేదు."
      : "Pest management guidance could not be loaded.",

    loadingGuidance: isTelugu
      ? "మార్గదర్శకాన్ని లోడ్ చేస్తోంది..."
      : "Loading guidance...",

    note: isTelugu
      ? "గమనిక: AI అంచనా సహాయక సమాచారం మాత్రమే. తుది వ్యవసాయ నిర్ణయాలకు స్థానిక వ్యవసాయ నిపుణుల సలహాను ఉపయోగించండి."
      : "Note: AI prediction is advisory information only. Use local agricultural guidance for final decisions.",
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    setResult(null);
    setGuidance(null);
    setError("");

    if (!selectedFile) {
      setFile(null);
      setPreview("");
      return;
    }

    if (!selectedFile.type.startsWith("image/")) {
      setFile(null);
      setPreview("");
      setError(text.invalidImage);
      return;
    }

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
  };

  const loadGuidance = async (pestName) => {
    setGuidanceLoading(true);

    try {
      const encodedPest = encodeURIComponent(
        pestName
      );

      const response = await fetch(
        `${API_BASE}/api/pest-guidance/${encodedPest}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || text.guidanceError
        );
      }

      setGuidance(data);
    } catch (err) {
      console.error(
        "PEST GUIDANCE ERROR:",
        err
      );

      setGuidance(null);

      setError(text.guidanceError);
    } finally {
      setGuidanceLoading(false);
    }
  };

  const detectPest = async () => {
    if (!file) {
      setError(text.uploadError);
      return;
    }

    setLoading(true);
    setGuidance(null);
    setError("");

    try {
      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        `${API_BASE}/api/pest/predict`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || text.serverError
        );
      }

      setResult(data);

      if (data.pest) {
        await loadGuidance(data.pest);
      }
    } catch (err) {
      console.error(
        "PEST DETECTION ERROR:",
        err
      );

      setResult(null);
      setGuidance(null);

      setError(text.serverError);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-card">
      <h1>{text.title}</h1>

      <p className="page-subtitle">
        {text.subtitle}
      </p>

      {/* ================================================== */}
      {/* IMAGE UPLOAD */}
      {/* ================================================== */}

      <div className="form-card">
        <label
          htmlFor="pest-image"
          className="upload-label"
        >
          {text.choose}
        </label>

        <input
          id="pest-image"
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
      </div>

      {/* ================================================== */}
      {/* IMAGE PREVIEW */}
      {/* ================================================== */}

      {preview && (
        <div className="result-card">
          <h2>{text.selected}</h2>

          <img
            src={preview}
            alt={isTelugu ? "ఎంచుకున్న పురుగు చిత్రం" : "Selected pest"}
            style={{
              width: "100%",
              maxWidth: "500px",
              maxHeight: "400px",
              objectFit: "contain",
              borderRadius: "12px",
              marginTop: "12px",
            }}
          />
        </div>
      )}

      {/* ================================================== */}
      {/* DETECT BUTTON */}
      {/* ================================================== */}

      <button
        type="button"
        onClick={detectPest}
        disabled={!file || loading}
        className="primary-btn"
        style={{
          marginTop: "16px",
        }}
      >
        {loading
          ? text.detecting
          : text.detect}
      </button>

      {/* ================================================== */}
      {/* ERROR */}
      {/* ================================================== */}

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

      {/* ================================================== */}
      {/* DETECTION RESULT */}
      {/* ================================================== */}

      {result && (
        <div
          className="result-card"
          style={{
            marginTop: "24px",
          }}
        >
          <h2>{text.result}</h2>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "16px",
              marginTop: "16px",
            }}
          >
            <div className="stat-card">
              <div className="stat-label">
                🐛 {text.pest}
              </div>

              <div className="stat-value">
                {translatePestName(result.pest, language)}
              </div>
            </div>

            {guidance?.crop && (
              <div className="stat-card">
                <div className="stat-label">
                  🌱 {text.crop}
                </div>

                <div className="stat-value">
                  {translateCropName(guidance.crop, language)}
                </div>
              </div>
            )}

            <div className="stat-card">
              <div className="stat-label">
                🎯 {text.confidence}
              </div>

              <div className="stat-value">
                {Number(
                  result.confidence
                ).toFixed(2)}
                %
              </div>
            </div>
          </div>

          {/* TOP 3 */}

          <h3
            style={{
              marginTop: "24px",
            }}
          >
            {text.top3}
          </h3>

          <div
            style={{
              marginTop: "12px",
            }}
          >
            {result.top3?.map(
              (item, index) => (
                <div
                  key={`${translatePestName(item.pest, language)}-${index}`}
                  style={{
                    display: "flex",
                    justifyContent:
                      "space-between",
                    alignItems: "center",
                    padding: "12px 0",
                    borderBottom:
                      "1px solid rgba(128,128,128,0.2)",
                  }}
                >
                  <span>
                    {index + 1}.{" "}
                    {translatePestName(item.pest, language)}
                  </span>

                  <strong>
                    {Number(
                      item.confidence
                    ).toFixed(2)}
                    %
                  </strong>
                </div>
              )
            )}
          </div>

          {/* CONFIDENCE WARNING */}

          <div
            style={{
              marginTop: "20px",
              padding: "14px",
              borderRadius: "10px",
              background:
                Number(result.confidence) < 70
                  ? "#fff3cd"
                  : "#e8f5e9",
              color:
                Number(result.confidence) < 70
                  ? "#664d03"
                  : "#1b5e20",
            }}
          >
            {Number(result.confidence) < 70
              ? text.warning
              : text.noWarning}
          </div>

          {/* ================================================== */}
          {/* GUIDANCE */}
          {/* ================================================== */}

          {guidanceLoading && (
            <div
              style={{
                marginTop: "24px",
              }}
            >
              <h2>
                {text.guidanceTitle}
              </h2>

              <p>
                {text.loadingGuidance}
              </p>
            </div>
          )}

          {guidance && !guidanceLoading && (
            <div
              style={{
                marginTop: "28px",
              }}
            >
              <h2>
                {text.guidanceTitle}
              </h2>

              <div
                className="result-card"
                style={{
                  marginTop: "16px",
                }}
              >
                {/* TYPE */}

                <h3>
                  {text.pestType}
                </h3>

                <p>
                  {translateGuidanceValue(guidance.type, "type", language)}
                </p>

                {/* SUMMARY */}

                <h3
                  style={{
                    marginTop: "20px",
                  }}
                >
                  {text.summary}
                </h3>

                <p>
                  {translateGuidanceValue(guidance.summary, "summary", language)}
                </p>

                {/* MANAGEMENT */}

                <h3
                  style={{
                    marginTop: "20px",
                  }}
                >
                  {text.management}
                </h3>

                <ol>
                  {guidance.management?.map(
                    (item, index) => (
                      <li
                        key={index}
                        style={{
                          marginBottom: "8px",
                        }}
                      >
                        {translateGuidanceValue(item, "management", language)}
                      </li>
                    )
                  )}
                </ol>

                {/* TREATMENT */}

                <h3
                  style={{
                    marginTop: "20px",
                  }}
                >
                  {text.treatment}
                </h3>

                <ol>
                  {guidance.treatment?.map(
                    (item, index) => (
                      <li
                        key={index}
                        style={{
                          marginBottom: "8px",
                        }}
                      >
                        {translateGuidanceValue(item, "treatment", language)}
                      </li>
                    )
                  )}
                </ol>

                {/* PESTICIDE POLICY */}

                <div
                  style={{
                    marginTop: "24px",
                    padding: "16px",
                    borderRadius: "10px",
                    background: "#fff3cd",
                    color: "#664d03",
                  }}
                >
                  <h3>
                    {text.pesticidePolicy}
                  </h3>

                  <p>
                    {translateGuidanceValue(guidance.pesticide_policy, "pesticide_policy", language)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ================================================== */}
      {/* NOTE */}
      {/* ================================================== */}

      <p
        style={{
          marginTop: "20px",
          fontSize: "13px",
          opacity: 0.75,
        }}
      >
        {text.note}
      </p>
    </div>
  );
}

export default PestDetection;