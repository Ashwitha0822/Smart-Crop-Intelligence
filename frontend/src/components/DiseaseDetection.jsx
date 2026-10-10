import React, { useEffect, useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

const translations = {
  en: {
    title: "Crop Disease Detection",
    description:
      "Upload a crop leaf image to detect possible diseases using AI.",
    chooseImage: "Choose Leaf Image",
    detectDisease: "Detect Disease",
    detecting: "Detecting Disease...",
    selectedImage: "Selected Image",
    result: "Detection Result",
    crop: "Crop",
    disease: "Disease",
    confidence: "Confidence",
    topPredictions: "Top 3 Predictions",
    uploadFirst: "Please select an image first.",
    failed: "Disease detection failed. Please try again.",
    guidanceFailed:
      "Disease was detected, but treatment guidance could not be loaded.",
    supported:
      "Currently supported crops: Apple, Maize, Grape and Orange.",
    note:
      "For best results, upload a clear leaf image with good lighting.",
    guidanceTitle: "Management & Treatment Guidance",
    diseaseType: "Disease Type",
    summary: "Summary",
    management: "Management Steps",
    treatment: "Treatment Guidance",
    pesticidePolicy: "Pesticide Safety Policy",
    loadingGuidance: "Searching agricultural sources and loading treatment guidance...",
    pesticideOptions: "Pesticide / Fungicide Options",
    pesticideOptionsNote:
      "These are candidate options, not a prescription. Confirm current registration and product-label claims for this crop and disease before use.",
    noLocalOptions:
      "No pesticide option is stored locally for this disease. Review the official search results below and confirm with an agricultural officer.",
    healthyNoPesticide:
      "The model classified this leaf as healthy. Do not apply disease pesticides unless a separate, confirmed problem requires them.",
    webResearchTitle: "Search results from official agricultural sources",
    webResearchNote:
      "Results are searched live from agricultural and government sources. Open the source and verify the crop, disease, registration, dose and safety instructions. Search results are not an automatic pesticide prescription.",
    noWebSources:
      "No results were returned from the configured official websites. Try again later or consult a local agricultural extension officer.",
    webSearchUnavailable:
      "Live web search is unavailable right now. The disease result is still shown, but verify treatment using an official agricultural source.",
    openSource: "Open source website",
    caution:
      "Always follow the product label and local agricultural guidance before using any pesticide.",
  },
  te: {
    title: "పంట వ్యాధి గుర్తింపు",
    description:
      "కృత్రిమ మేధస్సుతో పంటకు వచ్చే వ్యాధులను గుర్తించడానికి ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి.",
    chooseImage: "ఆకు చిత్రాన్ని ఎంచుకోండి",
    detectDisease: "వ్యాధిని గుర్తించండి",
    detecting: "వ్యాధిని గుర్తిస్తోంది...",
    selectedImage: "ఎంచుకున్న చిత్రం",
    result: "గుర్తింపు ఫలితం",
    crop: "పంట",
    disease: "వ్యాధి",
    confidence: "నమ్మక స్థాయి",
    topPredictions: "మొదటి 3 అంచనాలు",
    uploadFirst: "ముందుగా ఒక చిత్రాన్ని ఎంచుకోండి.",
    failed: "వ్యాధి గుర్తింపు విఫలమైంది. మళ్లీ ప్రయత్నించండి.",
    guidanceFailed:
      "వ్యాధి గుర్తించబడింది, కానీ చికిత్స మార్గదర్శకాలను లోడ్ చేయలేకపోయాము.",
    supported:
      "ప్రస్తుతం మద్దతు ఉన్న పంటలు: ఆపిల్, మొక్కజొన్న, ద్రాక్ష మరియు నారింజ.",
    note:
      "మంచి ఫలితాల కోసం మంచి వెలుతురులో తీసిన స్పష్టమైన ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి.",
    guidanceTitle: "వ్యాధి నిర్వహణ మరియు చికిత్స మార్గదర్శకాలు",
    diseaseType: "వ్యాధి రకం",
    summary: "సారాంశం",
    management: "నిర్వహణ చర్యలు",
    treatment: "చికిత్స మార్గదర్శకాలు",
    pesticidePolicy: "పురుగుమందుల భద్రతా సూచనలు",
    loadingGuidance: "వ్యవసాయ వెబ్‌సైట్లను వెతికి చికిత్స మార్గదర్శకాలను లోడ్ చేస్తోంది...",
    pesticideOptions: "పురుగుమందు / శిలీంధ్రనాశక ఎంపికలు",
    pesticideOptionsNote:
      "ఇవి పరిశీలించాల్సిన ఎంపికలు మాత్రమే; నేరుగా వినియోగ సూచన కాదు. వాడే ముందు ఈ పంటకు, వ్యాధికి ప్రస్తుత నమోదు మరియు ఉత్పత్తి లేబుల్‌ను నిర్ధారించండి.",
    noLocalOptions:
      "ఈ వ్యాధికి స్థానిక జాబితాలో మందుల ఎంపిక లేదు. క్రింది అధికారిక వెబ్‌సైట్ ఫలితాలను పరిశీలించి వ్యవసాయ అధికారితో నిర్ధారించండి.",
    healthyNoPesticide:
      "ఈ ఆకు ఆరోగ్యంగా ఉందని మోడల్ గుర్తించింది. వేరుగా నిర్ధారించిన సమస్య లేకపోతే వ్యాధి మందులను ఉపయోగించవద్దు.",
    webResearchTitle: "అధికారిక వ్యవసాయ వెబ్‌సైట్ల శోధన ఫలితాలు",
    webResearchNote:
      "వ్యవసాయ మరియు ప్రభుత్వ వెబ్‌సైట్లలో ప్రత్యక్షంగా శోధించబడిన ఫలితాలు ఇవి. పంట, వ్యాధి, నమోదు, మోతాదు మరియు భద్రతా సూచనలను మూల వెబ్‌సైట్‌లో నిర్ధారించండి. శోధన ఫలితం మాత్రమే పురుగుమందు వినియోగానికి తుది సిఫార్సు కాదు.",
    noWebSources:
      "ఎంచుకున్న అధికారిక వెబ్‌సైట్లలో ఫలితాలు లభించలేదు. కొంతసేపటి తర్వాత మళ్లీ ప్రయత్నించండి లేదా స్థానిక వ్యవసాయ విస్తరణ అధికారిని సంప్రదించండి.",
    webSearchUnavailable:
      "ప్రస్తుతం ప్రత్యక్ష వెబ్ శోధన అందుబాటులో లేదు. వ్యాధి ఫలితం చూపబడుతుంది; చికిత్సను అధికారిక వ్యవసాయ మూలం ద్వారా నిర్ధారించండి.",
    openSource: "మూల వెబ్‌సైట్‌ను తెరవండి",
    caution:
      "పురుగుమందును ఉపయోగించే ముందు ఉత్పత్తి లేబుల్ మరియు స్థానిక వ్యవసాయ మార్గదర్శకాలను తప్పనిసరిగా పాటించండి.",
  },
};

const cropTranslations = {
  Apple: "ఆపిల్",
  "Corn_(maize)": "మొక్కజొన్న",
  Grape: "ద్రాక్ష",
  Orange: "నారింజ",
};

const diseaseTranslations = {
  Apple_scab: "ఆపిల్ స్కాబ్",
  Black_rot: "బ్లాక్ రాట్",
  Cedar_apple_rust: "సీడార్ ఆపిల్ రస్ట్",
  healthy: "ఆరోగ్యకరమైనది",
  "Cercospora_leaf_spot Gray_leaf_spot":
    "సెర్కోస్పోరా లీఫ్ స్పాట్ / గ్రే లీఫ్ స్పాట్",
  Common_rust_: "కామన్ రస్ట్",
  Northern_Leaf_Blight: "నార్తర్న్ లీఫ్ బ్లైట్",
  "Esca_(Black_Measles)": "ఎస్కా (బ్లాక్ మీజిల్స్)",
  "Leaf_blight_(Isariopsis_Leaf_Spot)":
    "లీఫ్ బ్లైట్ (ఇసారియోప్సిస్ లీఫ్ స్పాట్)",
  "Haunglongbing_(Citrus_greening)":
    "హువాంగ్‌లాంగ్‌బింగ్ (సిట్రస్ గ్రీనింగ్)",
};

const diseaseTypeTranslations = {
  "fungal disease": "శిలీంధ్ర వ్యాధి",
  "fungal disease complex": "శిలీంధ్ర వ్యాధుల సముదాయం",
  healthy: "ఆరోగ్యకరమైనది",
  "bacterial-associated citrus disease":
    "బ్యాక్టీరియాతో సంబంధం ఉన్న సిట్రస్ వ్యాధి",
};

// Guidance strings returned by the backend are translated here when Telugu is selected.
const DISEASE_GUIDANCE_TE = {
  "fungal disease": "శిలీంధ్ర వ్యాధి",
  "northern leaf blight is a fungal disease that causes elongated lesions on maize leaves":
    "నార్తర్న్ లీఫ్ బ్లైట్ ఒక శిలీంధ్ర వ్యాధి. ఇది మొక్కజొన్న ఆకులపై పొడవైన మచ్చలను కలిగిస్తుంది.",
  "use resistant hybrids where available":
    "లభ్యమైతే వ్యాధిని తట్టుకునే హైబ్రిడ్ రకాలను సాగు చేయండి.",
  "practice crop rotation where suitable":
    "అనుకూలమైన చోట పంట మార్పిడిని పాటించండి.",
  "manage crop residue appropriately":
    "పంట అవశేషాలను సరైన పద్ధతిలో నిర్వహించండి.",
  "monitor the crop early so disease spread can be identified quickly":
    "వ్యాధి వ్యాప్తిని త్వరగా గుర్తించేందుకు పంటను తొలిదశ నుంచే పరిశీలించండి.",
  "this is a disease, not an insect pest":
    "ఇది కీటక పురుగు సమస్య కాదు; పంటకు వచ్చే వ్యాధి.",
  "use resistant varieties and cultural management first":
    "ముందుగా వ్యాధిని తట్టుకునే రకాలు, సరైన సాగు నిర్వహణ పద్ధతులను పాటించండి.",
  "where fungicide treatment is justified, use only a registered product labelled for northern leaf blight of maize":
    "శిలీంద్రనాశిని అవసరమని సిఫార్సు చేసినప్పుడు, మొక్కజొన్న నార్తర్న్ లీఫ్ బ్లైట్ కోసం నమోదైన ఉత్పత్తినే ఉపయోగించండి.",
  "follow label instructions, protective equipment requirements and harvest restrictions":
    "ఉత్పత్తి లేబుల్ సూచనలు, రక్షణ పరికరాల అవసరాలు, కోతకు ముందు పాటించాల్సిన నియమాలను అనుసరించండి.",
  "use only legally registered products labelled for the crop and diagnosed disease in your location. follow the product label, protective equipment requirements, application instructions and pre-harvest interval":
    "మీ ప్రాంతంలో ఆ పంటకు, నిర్ధారించిన వ్యాధికి చట్టబద్ధంగా నమోదైన ఉత్పత్తులనే ఉపయోగించండి. లేబుల్ సూచనలు, రక్షణ పరికరాలు, వినియోగ విధానం, కోతకు ముందు వేచి ఉండే వ్యవధిని తప్పనిసరిగా పాటించండి.",
  "no disease symptom was identified by the model":
    "AI మోడల్ ఎలాంటి వ్యాధి లక్షణాలను గుర్తించలేదు.",
  "continue regular crop monitoring":
    "పంటను క్రమం తప్పకుండా పరిశీలిస్తూ ఉండండి.",
  "maintain proper irrigation and balanced nutrition":
    "సరైన నీటి పారుదల మరియు సమతుల్య పోషకాలను అందించండి.",
  "keep the field clean and manage crop residue appropriately":
    "పొలాన్ని శుభ్రంగా ఉంచి, పంట అవశేషాలను సరైన పద్ధతిలో నిర్వహించండి.",
  "no disease treatment is indicated from this prediction":
    "ఈ అంచనా ప్రకారం వ్యాధికి ప్రత్యేక చికిత్స అవసరమని సూచించడం లేదు.",
  "avoid unnecessary pesticide applications":
    "అవసరం లేకుండా పురుగుమందులను ఉపయోగించవద్దు.",
};

const pesticideTranslations = {
  "Captan 50% WP": "క్యాప్టాన్ 50% WP",
  "Captan 75% WP": "క్యాప్టాన్ 75% WP",
  "Difenoconazole 25% EC": "డైఫెనోకోనజోల్ 25% EC",
  "Dodine 65% WP": "డోడిన్ 65% WP",
  "Mancozeb 75% WG": "మాంకోజెబ్ 75% WG",
  "Kresoxim-methyl 44.3% SC": "క్రెసాక్సిమ్-మిథైల్ 44.3% SC",
  Tebuconazole: "టెబుకోనాజోల్",
  Chlorothalonil: "క్లోరోథలోనిల్",
  Mancozeb: "మాంకోజెబ్",
  Zineb: "జినెబ్",
  "Propiconazole 25% EC": "ప్రోపికోనాజోల్ 25% EC",
};

function formatDiseaseName(name) {
  if (!name) return "--";

  return String(name)
    .replaceAll("_", " ")
    .replace(/\s+/g, " ")
    .trim();
}

function DiseaseDetection({ language = "en" }) {
  const text = translations[language] || translations.en;

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [guidance, setGuidance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [guidanceLoading, setGuidanceLoading] = useState(false);
  const [error, setError] = useState("");
  const [guidanceError, setGuidanceError] = useState("");

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0];

    setResult(null);
    setGuidance(null);
    setError("");
    setGuidanceError("");

    if (!selectedFile) {
      setFile(null);
      setPreview("");
      return;
    }

    if (!selectedFile.type.startsWith("image/")) {
      setFile(null);
      setPreview("");
      setError(
        language === "te"
          ? "దయచేసి JPG, JPEG లేదా PNG చిత్రాన్ని ఎంచుకోండి."
          : "Please select a JPG, JPEG or PNG image."
      );
      return;
    }

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
  }

  async function loadGuidance(crop, diagnosis) {
    setGuidanceLoading(true);
    setGuidanceError("");

    try {
      const response = await axios.get(
        `${API}/api/guidance/${encodeURIComponent(crop)}/${encodeURIComponent(diagnosis)}`
      );
      setGuidance(response.data);
    } catch (err) {
      console.error("GUIDANCE ERROR:", err);
      setGuidance(null);
      setGuidanceError(text.guidanceFailed);
    } finally {
      setGuidanceLoading(false);
    }
  }

  async function detectDisease() {
    if (!file) {
      setError(text.uploadFirst);
      return;
    }

    setLoading(true);
    setError("");
    setGuidance(null);
    setGuidanceError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const token = localStorage.getItem("token");
      const response = await axios.post(`${API}/api/disease/predict`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      const diseaseResult = response.data;
      setResult(diseaseResult);

      if (diseaseResult.success && diseaseResult.crop && diseaseResult.diagnosis) {
        await loadGuidance(diseaseResult.crop, diseaseResult.diagnosis);
      }
    } catch (err) {
      console.error("DISEASE ERROR:", err);
      setError(
        language === "te"
          ? text.failed
          : err.response?.data?.detail || text.failed
      );
    } finally {
      setLoading(false);
    }
  }

  function displayCrop(crop) {
    if (language === "te") return cropTranslations[crop] || crop || "--";
    if (crop === "Corn_(maize)") return "Maize";
    return crop || "--";
  }

  function displayDisease(disease) {
    if (language === "te") {
      return diseaseTranslations[disease] || formatDiseaseName(disease);
    }
    return formatDiseaseName(disease);
  }

  function displayDiseaseType(value) {
    if (!value) return "--";
    if (language !== "te") return value;
    return diseaseTypeTranslations[String(value).trim().toLowerCase()] || "పంట వ్యాధి";
  }

  function translateDiseaseGuidance(value, kind) {
    if (!value) return "--";
    if (language !== "te") return value;

    // If the backend already returned Telugu, keep it unchanged.
    if (/[\u0C00-\u0C7F]/.test(String(value))) return value;

    const key = String(value)
      .trim()
      .toLowerCase()
      .replace(/[’‘]/g, "'")
      .replace(/\s+/g, " ")
      .replace(/[.!?]+$/, "");

    if (DISEASE_GUIDANCE_TE[key]) return DISEASE_GUIDANCE_TE[key];

    // Safe Telugu fallback: never show an unknown English guidance sentence.
    const fallback = {
      type: "పంట వ్యాధి",
      summary:
        "ఈ వ్యాధి పంటకు నష్టం కలిగించవచ్చు. లక్షణాలను గమనించి స్థానిక వ్యవసాయ నిపుణుల సలహా తీసుకోండి.",
      management:
        "పంటను క్రమం తప్పకుండా పరిశీలించి, స్థానిక వ్యవసాయ సిఫార్సుల ప్రకారం నిర్వహణ చర్యలు తీసుకోండి.",
      treatment:
        "చికిత్స అవసరమైతే, మీ ప్రాంతంలో ఆ పంటకు మరియు నిర్ధారించిన వ్యాధికి అనుమతించబడిన ఉత్పత్తిని మాత్రమే లేబుల్ సూచనల ప్రకారం ఉపయోగించండి.",
      pesticide_policy:
        "పురుగుమందులు లేదా శిలీంద్రనాశకాలను అవసరమైనప్పుడే ఉపయోగించండి. చట్టబద్ధంగా నమోదైన ఉత్పత్తులనే వాడండి. లేబుల్, రక్షణ పరికరాలు, వినియోగ విధానం మరియు కోతకు ముందు వేచి ఉండే వ్యవధిని పాటించండి.",
    };

    return fallback[kind] || "వివరాలు అందుబాటులో లేవు.";
  }

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "24px" }}>
      <div className="panel" style={{ padding: "28px" }}>
        <h1>🦠 {text.title}</h1>
        <p>{text.description}</p>

        <div
          style={{
            padding: "14px",
            borderRadius: "10px",
            margin: "20px 0",
            background: "#f4f8f4",
          }}
        >
          {text.supported}
        </div>

        <label style={{ display: "block", fontWeight: "600", marginBottom: "8px" }}>
          📷 {text.chooseImage}
        </label>
        <input type="file" accept="image/png,image/jpeg,image/jpg" onChange={handleFileChange} />

        {preview && (
          <div style={{ marginTop: "20px" }}>
            <h3>{text.selectedImage}</h3>
            <img
              src={preview}
              alt={language === "te" ? "ఎంచుకున్న పంట ఆకు చిత్రం" : "Selected crop leaf"}
              style={{
                width: "100%",
                maxWidth: "450px",
                maxHeight: "400px",
                objectFit: "contain",
                borderRadius: "14px",
                border: "1px solid #ddd",
              }}
            />
          </div>
        )}

        <button
          className="primary"
          onClick={detectDisease}
          disabled={loading || !file}
          style={{ marginTop: "20px" }}
        >
          {loading ? `🔍 ${text.detecting}` : `🔍 ${text.detectDisease}`}
        </button>

        {error && (
          <div style={{ marginTop: "18px", padding: "12px", borderRadius: "10px", background: "#ffecec", color: "#a00000" }}>
            {error}
          </div>
        )}

        {result && (
          <div style={{ marginTop: "30px" }}>
            <h2>✅ {text.result}</h2>

            <div className="stats-grid" style={{ marginTop: "18px" }}>
              <div className="stat-card">
                <div className="stat-icon">🌱</div>
                <div>
                  <p className="stat-title">{text.crop}</p>
                  <h2>{displayCrop(result.crop)}</h2>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">🦠</div>
                <div>
                  <p className="stat-title">{text.disease}</p>
                  <h2>{displayDisease(result.diagnosis)}</h2>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">🎯</div>
                <div>
                  <p className="stat-title">{text.confidence}</p>
                  <h2>{Number(result.confidence).toFixed(2)}%</h2>
                </div>
              </div>
            </div>

            <div className="panel" style={{ marginTop: "24px" }}>
              <h3>{text.topPredictions}</h3>
              {result.top3?.map((item, index) => (
                <div
                  className="history"
                  key={`${item.crop}-${item.diagnosis}-${index}`}
                  style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}
                >
                  <span>
                    {displayCrop(item.crop)} — {displayDisease(item.diagnosis)}
                  </span>
                  <strong>{Number(item.confidence).toFixed(2)}%</strong>
                </div>
              ))}
            </div>

            {guidanceLoading && (
              <div className="panel" style={{ marginTop: "24px" }}>
                <h3>🌿 {text.loadingGuidance}</h3>
              </div>
            )}

            {guidanceError && (
              <div style={{ marginTop: "20px", padding: "14px", borderRadius: "10px", background: "#fff4e5" }}>
                {guidanceError}
              </div>
            )}

            {guidance?.guidance && (
              <div style={{ marginTop: "24px" }}>
                <div className="panel">
                  <h2>🌿 {text.guidanceTitle}</h2>
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                      gap: "16px",
                      marginTop: "18px",
                    }}
                  >
                    <div style={{ padding: "16px", borderRadius: "12px", background: "#f7faf7" }}>
                      <strong>{text.diseaseType}</strong>
                      <p>{displayDiseaseType(guidance.guidance.disease_type)}</p>
                    </div>
                    <div style={{ padding: "16px", borderRadius: "12px", background: "#f7faf7" }}>
                      <strong>{text.summary}</strong>
                      <p>{translateDiseaseGuidance(guidance.guidance.summary, "summary")}</p>
                    </div>
                  </div>
                </div>

                <div className="panel" style={{ marginTop: "18px" }}>
                  <h3>🌱 {text.management}</h3>
                  <ol>
                    {guidance.guidance.management?.map((item, index) => (
                      <li key={index} style={{ marginBottom: "10px" }}>
                        {translateDiseaseGuidance(item, "management")}
                      </li>
                    ))}
                  </ol>
                </div>

                <div className="panel" style={{ marginTop: "18px" }}>
                  <h3>🧪 {text.treatment}</h3>
                  <ol>
                    {guidance.guidance.treatment?.map((item, index) => (
                      <li key={index} style={{ marginBottom: "10px" }}>
                        {translateDiseaseGuidance(item, "treatment")}
                      </li>
                    ))}
                  </ol>
                </div>

                <div className="panel" style={{ marginTop: "18px" }}>
                  <h3>🧪 {text.pesticideOptions}</h3>
                  {guidance.pesticide_recommendations?.length > 0 ? (
                    <>
                      <ul>
                        {guidance.pesticide_recommendations.map((item, index) => (
                          <li key={index} style={{ marginBottom: "8px" }}>
                            {language === "te" ? pesticideTranslations[item] || item : item}
                          </li>
                        ))}
                      </ul>
                      <p>{text.pesticideOptionsNote}</p>
                    </>
                  ) : (
                    <p>
                      {guidance.diagnosis?.toLowerCase() === "healthy"
                        ? text.healthyNoPesticide
                        : text.noLocalOptions}
                    </p>
                  )}
                </div>

                <div className="panel" style={{ marginTop: "18px" }}>
                  <h3>🌐 {text.webResearchTitle}</h3>
                  <p>{text.webResearchNote}</p>
                  {guidance.web_sources?.length > 0 ? (
                    <ol>
                      {guidance.web_sources.map((source, index) => (
                        <li key={source.url || index} style={{ marginBottom: "16px" }}>
                          <a href={source.url} target="_blank" rel="noreferrer">
                            {language === "te" ? source.domain : source.title}
                          </a>
                          {language === "en" && source.snippet ? (
                            <p style={{ marginTop: "6px" }}>{source.snippet}</p>
                          ) : (
                            <p style={{ marginTop: "6px" }}>
                              {language === "te"
                                ? "ఈ అధికారిక మూలంలో పంట వ్యాధి నిర్వహణ సమాచారం ఉంది. వివరాలను మూల వెబ్‌సైట్‌లో పరిశీలించండి."
                                : "Open the source to review the relevant guidance."}
                            </p>
                          )}
                        </li>
                      ))}
                    </ol>
                  ) : (
                    <p>
                      {guidance.web_search_status === "healthy"
                        ? text.healthyNoPesticide
                        : guidance.web_search_status === "search_error" || guidance.web_search_status === "not_installed"
                          ? text.webSearchUnavailable
                          : text.noWebSources}
                    </p>
                  )}
                </div>

                <div className="panel" style={{ marginTop: "18px", border: "1px solid #e6d7a8" }}>
                  <h3>⚠️ {text.pesticidePolicy}</h3>
                  <p>{translateDiseaseGuidance(guidance.pesticide_policy, "pesticide_policy")}</p>
                  <p style={{ marginTop: "12px", fontWeight: "600" }}>{text.caution}</p>
                </div>
              </div>
            )}

            <p style={{ marginTop: "20px", color: "#666" }}>{text.note}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default DiseaseDetection;
