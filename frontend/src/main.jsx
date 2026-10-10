import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import axios from "axios";
import DiseaseDetection from "./components/DiseaseDetection";
import ResearchAssistant from "./components/ResearchAssistant";
import PestDetection from "./components/PestDetection";
import VoiceAssistant from "./components/VoiceAssistant";
import { translations } from "./i18n/translations";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./style.css";

const API = "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: API,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// ============================================================
// TRANSLATIONS
// ============================================================

const cropTranslations = {
  apple: "ఆపిల్",
  banana: "అరటి",
  blackgram: "మినుములు",
  chickpea: "శనగ",
  coconut: "కొబ్బరి",
  coffee: "కాఫీ",
  cotton: "పత్తి",
  grapes: "ద్రాక్ష",
  jute: "జనపనార",
  kidneybeans: "రాజ్మా",
  lentil: "మసూర్ పప్పు",
  maize: "మొక్కజొన్న",
  mango: "మామిడి",
  mothbeans: "మోత్ బీన్స్",
  mungbean: "పెసలు",
  muskmelon: "ఖర్బూజ",
  orange: "నారింజ",
  papaya: "బొప్పాయి",
  pigeonpeas: "కందులు",
  pomegranate: "దానిమ్మ",
  rice: "వరి",
  watermelon: "పుచ్చకాయ",
};

// ============================================================
// APP
// ============================================================

function App() {
  const savedUser = JSON.parse(
    localStorage.getItem("user") || "null"
  );

  const savedLanguage =
    localStorage.getItem("language") || "en";

  const [user, setUser] = useState(savedUser);

  const [page, setPage] = useState(
    savedUser ? "dashboard" : "login"
  );

  const [language, setLanguage] =
    useState(savedLanguage);

  const [result, setResult] = useState(null);
  const [health, setHealth] = useState(null);
  const [satelliteHealth, setSatelliteHealth] =
    useState(null);

  const [history, setHistory] = useState([]);
  const [healthHistory, setHealthHistory] =
    useState([]);

  const [weather, setWeather] = useState(null);

  const [form, setForm] = useState({
    N: 90,
    P: 42,
    K: 43,
    temperature: 25,
    humidity: 80,
    ph: 6.5,
    rainfall: 200,
  });

  const [login, setLogin] = useState({
    email: "",
    password: "",
  });

  const [reg, setReg] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [ndvi, setNdvi] = useState(0.65);

  const [latitude, setLatitude] =
    useState(17.3850);

  const [longitude, setLongitude] =
    useState(78.4867);

  const [satelliteLoading, setSatelliteLoading] =
    useState(false);
  

  // ==========================================================
  // TRANSLATION
  // ==========================================================

  const t = (key) => {
    return (
      translations[language]?.[key] ||
      translations.en[key] ||
      key
    );
  };

  function changeLanguage(value) {
    setLanguage(value);
    localStorage.setItem("language", value);
  }


  function translateHealthStatus(status) {
  if (status === "Healthy") {
    return t("healthy");
  }

  if (status === "Moderate") {
    return t("moderate");
  }

  if (status === "Poor") {
    return t("poor");
  }

  return status || "--";
}

    function translateCropName(crop) {
  if (!crop) {
    return "--";
  }

  if (language === "te") {
    return (
      cropTranslations[
        crop.toLowerCase()
      ] || crop
    );
  }

  return crop;
}

function translateFieldName(key) {
  const fieldTranslations = {
    N: language === "te" ? "నత్రజని (N)" : "Nitrogen (N)",
    P: language === "te" ? "భాస్వరం (P)" : "Phosphorus (P)",
    K: language === "te" ? "పొటాషియం (K)" : "Potassium (K)",
    temperature: language === "te" ? "ఉష్ణోగ్రత" : "Temperature",
    humidity: language === "te" ? "తేమ" : "Humidity",
    ph: language === "te" ? "pH విలువ" : "pH",
    rainfall: language === "te" ? "వర్షపాతం" : "Rainfall",
  };

  return fieldTranslations[key] || key;
}
function translateCityName(city) {
  if (!city) {
    return "--";
  }

  if (
    language === "te" &&
    city.toLowerCase() === "hyderabad"
  ) {
    return "హైదరాబాద్";
  }

  return city;
}

function translateWeatherDescription(description) {
  if (!description || language === "en") {
    return description || "--";
  }

  const value = String(description).toLowerCase();

  // Clear sky
  if (value.includes("clear sky") || value === "clear") {
    return t("weatherClearSky");
  }

  // Clouds
  if (value.includes("few clouds")) {
    return t("weatherFewClouds");
  }

  if (value.includes("scattered clouds")) {
    return t("weatherScatteredClouds");
  }

  if (value.includes("broken clouds")) {
    return t("weatherBrokenClouds");
  }

  if (value.includes("overcast")) {
    return t("weatherOvercast");
  }

  // Thunderstorm
  if (value.includes("thunderstorm")) {
    return t("weatherThunderstorm");
  }

  // Rain
  if (value.includes("very heavy rain")) {
    return t("weatherVeryHeavyRain");
  }

  if (value.includes("heavy rain")) {
    return t("weatherHeavyRain");
  }

  if (value.includes("moderate rain")) {
    return t("weatherModerateRain");
  }

  if (value.includes("light rain")) {
    return t("weatherLightRain");
  }

  if (value === "rain" || value.includes("rain")) {
    return t("weatherRain");
  }

  // Drizzle
  if (value.includes("drizzle")) {
    return t("weatherDrizzle");
  }

  // Mist / Fog / Haze
  if (value.includes("mist")) {
    return t("weatherMist");
  }

  if (value.includes("fog")) {
    return t("weatherFog");
  }

  if (value.includes("haze")) {
    return t("weatherHaze");
  }

  // Dust / Smoke / Sand
  if (value.includes("dust")) {
    return t("weatherDust");
  }

  if (value.includes("smoke")) {
    return t("weatherSmoke");
  }

  if (value.includes("sand")) {
    return t("weatherSand");
  }

  // Snow
  if (value.includes("heavy snow")) {
    return t("weatherHeavySnow");
  }

  if (value.includes("light snow")) {
    return t("weatherLightSnow");
  }

  if (value.includes("snow")) {
    return t("weatherSnow");
  }

  // Squalls / Tornado
  if (value.includes("squall")) {
    return t("weatherSqualls");
  }

  if (value.includes("tornado")) {
    return t("weatherTornado");
  }

  return description;
}
function translateHealthNote(note) {
  if (!note || language === "en") {
    return note || "--";
  }

  const value = String(note).toLowerCase();

  if (value.includes("healthy")) {
    return "ఈ పంట ఆరోగ్యంగా ఉంది.";
  }
  if (value.includes("moderate")) {
    return "పంట ఆరోగ్యం మధ్యస్థ స్థాయిలో ఉంది. పంటను గమనిస్తూ అవసరమైన సంరక్షణ చర్యలు తీసుకోండి.";
  }
  if (value.includes("poor")) {
    return "పంట ఆరోగ్యం బలహీనంగా ఉంది. పొలాన్ని పరిశీలించి అవసరమైన చర్యలు తీసుకోండి.";
  }

  return note;
}

  // ==========================================================
  // LOGOUT
  // ==========================================================

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    setUser(null);
    setPage("login");

    setResult(null);
    setHealth(null);
    setSatelliteHealth(null);
    setHistory([]);
    setHealthHistory([]);
    setWeather(null);
  }

  // ==========================================================
  // REGISTER
  // ==========================================================

  async function registerUser() {
    try {
      const response = await client.post(
        "/api/auth/register",
        {
          name: reg.name,
          email: reg.email,
          password: reg.password,
        }
      );

      alert(
        response.data.message ||
          t("registrationSuccess")
      );

      setLogin({
        email: reg.email,
        password: reg.password,
      });

      setReg({
        name: "",
        email: "",
        password: "",
      });

      setPage("login");
    } catch (error) {
      console.error(
        "REGISTER ERROR:",
        error.response?.data || error
      );

      alert(
        error.response?.data?.detail ||
          t("registrationFailed")
      );
    }
  }

  // ==========================================================
  // LOGIN
  // ==========================================================

  async function loginUser() {
    try {
      const body = new URLSearchParams();

      body.append("username", login.email);
      body.append("password", login.password);

      const response = await client.post(
        "/api/auth/login",
        body,
        {
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
          },
        }
      );

      const token =
        response.data.access_token;

      if (!token) {
        throw new Error(
          "Access token was not returned."
        );
      }

      localStorage.setItem(
        "token",
        token
      );

      const loggedInUser = {
        email: login.email,
        name: login.email.split("@")[0],
      };

      localStorage.setItem(
        "user",
        JSON.stringify(loggedInUser)
      );

      setUser(loggedInUser);
      setPage("dashboard");

      setLogin({
        email: "",
        password: "",
      });
    } catch (error) {
      console.error(
        "LOGIN ERROR:",
        error.response?.data || error
      );

      alert(
        error.response?.data?.detail ||
          error.message ||
          t("loginFailed")
      );
    }
  }

  // ==========================================================
  // CROP RECOMMENDATION
  // ==========================================================

  async function recommend() {
    try {
      const input = {
        N: Number(form.N),
        P: Number(form.P),
        K: Number(form.K),
        temperature: Number(
          form.temperature
        ),
        humidity: Number(form.humidity),
        ph: Number(form.ph),
        rainfall: Number(form.rainfall),
      };

      const response =
        await client.post(
          "/api/recommendation",
          input
        );

      setResult(response.data);

      await loadHistory();
    } catch (error) {
      console.error(
        "RECOMMENDATION ERROR:",
        error.response?.data || error
      );

      alert(
        error.response?.data?.detail ||
          t("cropRecommendationFailed")
      );
    }
  }

  // ==========================================================
  // MANUAL NDVI
  // ==========================================================

  async function analyzeHealth() {
    try {
      const response =
        await client.post(
          "/api/health",
          {
            ndvi: Number(ndvi),
          }
        );

      setHealth(response.data);
      setSatelliteHealth(null);

      await loadHealthHistory();
    } catch (error) {
      console.error(
        "HEALTH ERROR:",
        error.response?.data || error
      );

      alert(
        error.response?.data?.detail ||
          t("healthAnalysisFailed")
      );
    }
  }

  // ==========================================================
  // SATELLITE NDVI
  // ==========================================================

  async function analyzeSatelliteHealth() {
    try {
      setSatelliteLoading(true);
      setSatelliteHealth(null);

      const response =
        await client.post(
          "/api/health/satellite",
          {
            latitude: Number(latitude),
            longitude: Number(longitude),
          }
        );

      if (
        response.data.success === false
      ) {
        alert(
          response.data.message ||
            t("satelliteAnalysisFailed")
        );
        return;
      }

      setSatelliteHealth(
        response.data
      );

      setHealth(
        response.data
      );

      await loadHealthHistory();
    } catch (error) {
      console.error(
        "SATELLITE ERROR:",
        error.response?.data || error
      );

      alert(
        error.response?.data?.message ||
          error.response?.data?.detail ||
          t("satelliteAnalysisFailed")
      );
    } finally {
      setSatelliteLoading(false);
    }
  }

  // ==========================================================
  // RECOMMENDATION HISTORY
  // ==========================================================

  async function loadHistory() {
    try {
      const response =
        await client.get(
          "/api/recommendation/history"
        );

      setHistory(
        Array.isArray(response.data)
          ? response.data
          : []
      );
    } catch (error) {
      console.error(
        "HISTORY ERROR:",
        error.response?.data || error
      );

      setHistory([]);
    }
  }

  // ==========================================================
  // NDVI HISTORY
  // ==========================================================

  async function loadHealthHistory() {
    try {
      const response =
        await client.get(
          "/api/health/history"
        );

      setHealthHistory(
        Array.isArray(
          response.data.history
        )
          ? response.data.history
          : []
      );
    } catch (error) {
      console.error(
        "HEALTH HISTORY ERROR:",
        error.response?.data || error
      );

      setHealthHistory([]);
    }
  }

  // ==========================================================
  // WEATHER
  // ==========================================================

  async function loadWeather() {
    try {
      const response =
        await client.get(
          "/api/weather?city=Hyderabad"
        );

      setWeather(response.data);
    } catch (error) {
      console.error(
        "WEATHER ERROR:",
        error.response?.data || error
      );

      setWeather(null);
    }
  }

  // ==========================================================
  // LATEST HEALTH
  // ==========================================================

  async function loadLatestHealth() {
    try {
      const response =
        await client.get(
          "/api/health/latest"
        );

      if (response.data.available) {
        setHealth(response.data);
      } else {
        setHealth(null);
      }
    } catch (error) {
      console.error(
        "LATEST HEALTH ERROR:",
        error.response?.data || error
      );

      setHealth(null);
    }
  }

  // ==========================================================
  // DASHBOARD
  // ==========================================================

  async function openDashboard() {
    setPage("dashboard");

    await Promise.all([
      loadHistory(),
      loadHealthHistory(),
      loadWeather(),
      loadLatestHealth(),
    ]);
  }

  // ==========================================================
  // PAGE LOADING
  // ==========================================================

  useEffect(() => {
    if (!user) {
      return;
    }

    if (page === "dashboard") {
      loadHistory();
      loadHealthHistory();
      loadWeather();
      loadLatestHealth();
    }

    if (page === "health") {
      loadHealthHistory();
      loadLatestHealth();
    }
  }, [user, page]);

  // ==========================================================
  // LOGIN
  // ==========================================================

  if (page === "login") {
    return (
      <Auth
        title={t("welcomeBack")}
        fields={login}
        setFields={setLogin}
        action={loginUser}
        switcher={() => setPage("register")}
        language={language}
        changeLanguage={changeLanguage}
        t={t}
      />
    );
  }

  // ==========================================================
  // REGISTER
  // ==========================================================

  if (page === "register") {
    return (
      <Auth
        title={t("createAccount")}
        fields={reg}
        setFields={setReg}
        action={registerUser}
        register
        switcher={() => setPage("login")}
        language={language}
        changeLanguage={changeLanguage}
        t={t}
      />
    );
  }

  // ==========================================================
  // MAIN APPLICATION
  // ==========================================================

  return (
    <div className="app">

      {/* HEADER */}

      <header>
        <div className="brand">
          🌾 {t("appName")}
        </div>

        <nav>

          <button onClick={openDashboard}>
            {t("dashboard")}
          </button>

          <button
            onClick={() =>
              setPage("recommend")
            }
          >
            🌱 {t("cropAI")}
          </button>

          <button
            onClick={() => {
              setPage("history");
              loadHistory();
            }}
          >
            📜 {t("history")}
          </button>

          <button
            onClick={() =>
              setPage("health")
            }
          >
            🌿 {t("cropHealth")}
          </button>

          <button
            onClick={() =>
              setPage("disease")
            }
          >
            🦠 {t("diseaseDetection")}
          </button>

          <button
            onClick={() =>
              setPage("pest")
            }
>
            🐛 {t("pestDetection")}
          </button>
          <button
            onClick={() =>
              setPage("research")
            }
>
            🤖 {t("research")}
          </button>
          <button
            onClick={() =>
              setPage("voice")
            }
>
            🎤 {t("voiceAssistant")}
          </button>

          <button
            onClick={() => {
              setPage("weather");
              loadWeather();
            }}
          >
            🌤️ {t("weather")}
          </button>

          <select
            value={language}
            onChange={(e) =>
              changeLanguage(
                e.target.value
              )
            }
          >
            <option value="en">
              🇬🇧 English
            </option>

            <option value="te">
              🇮🇳 తెలుగు
            </option>
          </select>

          <button onClick={logout}>
            {t("logout")}
          </button>

        </nav>
      </header>

      <main>

        {/* ================================================== */}
        {/* DASHBOARD */}
        {/* ================================================== */}

        {page === "dashboard" && (
          <div className="dashboard">

            <div className="dashboard-heading">

              <div>
                <h1>
                  {t("welcome")},{" "}
                  {user?.name ||
                    t("farmer")} 👋
                </h1>

                <p>
                  {t(
                    "dashboardDescription"
                  )}
                </p>
              </div>

              <div className="dashboard-icon">
                🌾
              </div>

            </div>

            <div className="stats-grid">

              <StatCard
                icon="🌱"
                title={t(
                  "recommendations"
                )}
                value={history.length}
                description={t(
                  "savedPredictions"
                )}
              />

              <StatCard
                icon="🌿"
                title={t("health")}
                value={
                  health
                    ? translateHealthStatus(
                        health.health_status
                      )
                    : t("notAnalyzed")
                }
                description={
                  health
                    ? `NDVI: ${Number(
                        health.ndvi
                      ).toFixed(2)}`
                    : t(
                        "analyzeCropHealth"
                      )
                }
              />

              <StatCard
                icon="🌡️"
                title={t(
                  "temperature"
                )}
                value={
                  weather
                    ? `${weather.temperature} °C`
                    : "--"
                }
                description={language === "te" ? "హైదరాబాద్" : "Hyderabad"}
              />

              <StatCard
                icon="💧"
                title={t("humidity")}
                value={
                  weather
                    ? `${weather.humidity}%`
                    : "--"
                }
                description={t(
                  "currentHumidity"
                )}
              />

            </div>

            <div className="dashboard-grid">

              <section className="dashboard-panel">

                <h2>
                  🌱{" "}
                  {t(
                    "aiCropRecommendation"
                  )}
                </h2>

                <p>
                  {t(
                    "recommendationDescription"
                  )}
                </p>

                {history.length > 0 ? (
                  <div className="dashboard-result">

                    <h3>
                      {t(
                        "latestRecommendation"
                      )}
                    </h3>

                    <div className="big-value">
                      🌾{" "}
                      {translateCropName(
                        history[
                            history.length - 1
                        ].crop||
                        history[
                            history.length - 1
                        ].recommended_crop
                      )}
                    </div>

                    <p>
                      {t("confidence")}:{" "}
                      {(
                        Number(
                          history[
                            history.length - 1
                          ].confidence
                        ) * 100
                      ).toFixed(1)}
                      %
                    </p>

                  </div>
                ) : (
                  <div className="dashboard-empty">
                    {t(
                      "noRecommendation"
                    )}
                  </div>
                )}

                <button
                  className="primary"
                  onClick={() =>
                    setPage("recommend")
                  }
                >
                  {t("openCropAI")}
                </button>

              </section>

              <section className="dashboard-panel">

                <h2>
                  🌤️{" "}
                  {t(
                    "currentWeather"
                  )}
                </h2>

                {weather ? (
                  <div className="weather-main">

                    <h3>
                      {translateCityName(weather.city)}
                    </h3>

                    <div className="weather-temp">
                      {weather.temperature}°C
                    </div>

                    <p>
                      {translateWeatherDescription(weather.description)}
                    </p>

                    <div className="weather-details">
                      <span>
                        💧{" "}
                        {t(
                          "humidity"
                        )}
                        :{" "}
                        {weather.humidity}%
                      </span>
                    </div>

                  </div>
                ) : (
                  <div className="dashboard-empty">
                    {t(
                      "weatherNotLoaded"
                    )}
                  </div>
                )}

                <button
                  className="primary"
                  onClick={() => {
                    setPage("weather");
                    loadWeather();
                  }}
                >
                  {t("viewWeather")}
                </button>

              </section>

              <section className="dashboard-panel">

                <h2>
                  🛰️{" "}
                  {t(
                    "satelliteCropHealth"
                  )}
                </h2>

                {health ? (
                  <div className="health-main">

                    <div className="big-value">
                      {translateHealthStatus(
                        health.health_status
                      )}
                    </div>

                    <p>
                      NDVI:{" "}
                      {Number(
                        health.ndvi
                      ).toFixed(4)}
                    </p>

                  </div>
                ) : (
                  <div className="dashboard-empty">
                    {t(
                      "noSatelliteAnalysis"
                    )}
                  </div>
                )}

                <button
                  className="primary"
                  onClick={() =>
                    setPage("health")
                  }
                >
                  {t(
                    "openCropHealth"
                  )}
                </button>

              </section>

              <section className="dashboard-panel">

                <h2>
                  ⚡{" "}
                  {t("quickActions")}
                </h2>

                <div className="quick-actions">

                  <button
                    onClick={() =>
                      setPage("recommend")
                    }
                  >
                    🌱{" "}
                    {t(
                      "newRecommendation"
                    )}
                  </button>

                  <button
                    onClick={() =>
                      setPage("health")
                    }
                  >
                    🛰️{" "}
                    {t(
                      "analyzeSatelliteNDVI"
                    )}
                  </button>

                  <button
                    onClick={() => {
                      setPage("weather");
                      loadWeather();
                    }}
                  >
                    🌤️{" "}
                    {t(
                      "checkWeather"
                    )}
                  </button>

                  <button
                    onClick={() => {
                      setPage("history");
                      loadHistory();
                    }}
                  >
                    📜{" "}
                    {t(
                      "viewHistory"
                    )}
                  </button>

                </div>

              </section>

            </div>
          </div>
        )}

        {/* ================================================== */}
        {/* CROP AI */}
        {/* ================================================== */}

        {page === "recommend" && (
          <section>

            <h2>
              🌱{" "}
              {t(
                "aiCropRecommendation"
              )}
            </h2>

            <p>
              {t(
                "enterSoilValues"
              )}
            </p>

            <div className="grid">

              {Object.keys(form).map(
                (key) => (
                  <label key={key}>

                    {translateFieldName(key)}

                    <input
                      type="number"
                      step="any"
                      value={form[key]}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          [key]:
                            e.target.value,
                        })
                      }
                    />

                  </label>
                )
              )}

            </div>

            <button
              className="primary"
              onClick={recommend}
            >
              {t(
                "recommendCrop"
              )}
            </button>

            {result && (
              <div className="result">

                <h2>
                  🌾{" "}
                  {translateCropName(result.recommended_crop)}
                </h2>

                <p>
                  {t("confidence")}:{" "}
                  {(
                    Number(
                      result.confidence
                    ) * 100
                  ).toFixed(2)}
                  %
                </p>

                <h3>
                  {t(
                    "top3Predictions"
                  )}
                </h3>

                {Array.isArray(
                  result.top3
                ) &&
                  result.top3.map(
                    (item, index) => (
                      <p
                        key={`${translateCropName(item.crop)}-${index}`}
                      >
                        <strong>
                          {translateCropName(item.crop)}
                        </strong>
                        :{" "}
                        {(
                          Number(
                            item.probability
                          ) * 100
                        ).toFixed(2)}
                        %
                      </p>
                    )
                  )}

              </div>
            )}

          </section>
        )}

        {/* ================================================== */}
        {/* CROP HEALTH */}
        {/* ================================================== */}

        {page === "health" && (
          <section>

            <h2>
              🛰️{" "}
              {t(
                "satelliteCropHealth"
              )}
            </h2>

            <p>
              {t(
                "satelliteDescription"
              )}
            </p>

            {/* FARM LOCATION */}

            <div className="panel">

              <h3>
                📍{" "}
                {t("farmLocation")}
              </h3>

              <p>
                {t(
                  "locationDescription"
                )}
              </p>

              <div className="grid">

                <label>

                  {t("latitude")}

                  <input
                    type="number"
                    step="any"
                    min="-90"
                    max="90"
                    value={latitude}
                    onChange={(e) =>
                      setLatitude(
                        e.target.value
                      )
                    }
                  />

                </label>

                <label>

                  {t("longitude")}

                  <input
                    type="number"
                    step="any"
                    min="-180"
                    max="180"
                    value={longitude}
                    onChange={(e) =>
                      setLongitude(
                        e.target.value
                      )
                    }
                  />

                </label>

              </div>

              <button
                className="primary"
                onClick={
                  analyzeSatelliteHealth
                }
                disabled={
                  satelliteLoading
                }
              >
                {satelliteLoading
                  ? `🛰️ ${t(
                      "analyzingSatellite"
                    )}`
                  : `🛰️ ${t(
                      "analyzeSatelliteNDVI"
                    )}`}
              </button>

            </div>

            {/* SATELLITE RESULT */}

            {satelliteHealth && (
              <div className="result">

                <h2>
                  🌿{" "}
                  {t(
                    "satelliteCropHealth"
                  )}
                </h2>

                <div className="big-value">
                  {translateHealthStatus(
                    satelliteHealth.health_status
                  )}
                </div>

                <p>
                  <strong>
                    {t("ndvi")}:
                  </strong>{" "}
                  {Number(
                    satelliteHealth.ndvi
                  ).toFixed(4)}
                </p>

                {satelliteHealth.vegetation_percentage !==
                  undefined && (
                  <p>
                    <strong>
                      🌿{" "}
                      {t(
                        "vegetationCoverage"
                      )}
                      :
                    </strong>{" "}
                    {
                      satelliteHealth
                        .vegetation_percentage
                    }%
                  </p>
                )}

                <p>
                  <strong>
                    🛰️{" "}
                    {t(
                      "pixelsAnalyzed"
                    )}
                    :
                  </strong>{" "}
                  {
                    satelliteHealth
                      .pixels_analyzed
                  }
                </p>

                <p>
                  <strong>
                    {t(
                      "noDataPixels"
                    )}
                    :
                  </strong>{" "}
                  {
                    satelliteHealth
                      .no_data_pixels
                  }
                </p>

                <p>
                  <strong>
                    📍{" "}
                    {t("latitude")}:
                  </strong>{" "}
                  {
                    satelliteHealth.latitude
                  }
                </p>

                <p>
                  <strong>
                    📍{" "}
                    {t("longitude")}:
                  </strong>{" "}
                  {
                    satelliteHealth.longitude
                  }
                </p>

                {satelliteHealth.analysis_period && (
                  <>
                    <p>
                      <strong>
                        📅{" "}
                        {t(
                          "analysisFrom"
                        )}
                        :
                      </strong>{" "}
                      {
                        satelliteHealth
                          .analysis_period
                          .from
                      }
                    </p>

                    <p>
                      <strong>
                        📅{" "}
                        {t(
                          "analysisTo"
                        )}
                        :
                      </strong>{" "}
                      {
                        satelliteHealth
                          .analysis_period
                          .to
                      }
                    </p>
                  </>
                )}

                <p>
                  🛰️{" "}
                  {t(
                    "sentinelAnalysis"
                  )}
                </p>

              </div>
            )}

            {/* ================================================= */}
            {/* NDVI HISTORY */}
            {/* ================================================= */}

            <div className="panel">

              <h3>
                📈{" "}
                {t("ndviHistory")}
              </h3>

              <p>
                {t(
                  "ndviHistoryDescription"
                )}
              </p>

              {healthHistory.length === 0 ? (
                <p>
                  {t(
                    "noNDVIHistory"
                  )}
                </p>
              ) : (
                <>
                  {/* SUMMARY */}

                  <div className="stats-grid">

                    <StatCard
                      icon="🌿"
                      title={t(
                        "latestNDVI"
                      )}
                      value={Number(
                        healthHistory[
                          healthHistory.length -
                            1
                        ].ndvi
                      ).toFixed(4)}
                      description={translateHealthStatus(
                        healthHistory[
                          healthHistory.length -
                            1
                        ].health_status
                      )}
                    />

                    <StatCard
                      icon="📊"
                      title={t(
                        "averageNDVI"
                      )}
                      value={(
                        healthHistory.reduce(
                          (
                            total,
                            item
                          ) =>
                            total +
                            Number(
                              item.ndvi
                            ),
                          0
                        ) /
                        healthHistory.length
                      ).toFixed(4)}
                      description={t("allAnalyses")}
                    />

                    <StatCard
                      icon="⬆️"
                      title={t(
                        "highestNDVI"
                      )}
                      value={Math.max(
                        ...healthHistory.map(
                          (item) =>
                            Number(
                              item.ndvi
                            )
                        )
                      ).toFixed(4)}
                      description={t(
                        "highestNDVI"
                      )}
                    />

                    <StatCard
                      icon="🔎"
                      title={t(
                        "totalAnalyses"
                      )}
                      value={
                        healthHistory.length
                      }
                      description={t(
                        "totalAnalyses"
                      )}
                    />

                  </div>

                  {/* LINE CHART */}

                  <div
                    style={{
                      width: "100%",
                      height: 350,
                      marginTop: 25,
                    }}
                  >
                    <ResponsiveContainer
                      width="100%"
                      height="100%"
                    >
                      <LineChart
                        data={healthHistory.map(
                          (
                            item,
                            index
                          ) => ({
                            date:
                              item.created_at
                                ? new Date(
                                    item.created_at
                                  ).toLocaleDateString()
                                : `Analysis ${
                                    index + 1
                                  }`,
                            ndvi: Number(
                              item.ndvi
                            ),
                          })
                        )}
                        margin={{
                          top: 10,
                          right: 30,
                          left: 10,
                          bottom: 20,
                        }}
                      >

                        <CartesianGrid
                          strokeDasharray="3 3"
                        />

                        <XAxis
                          dataKey="date"
                          tick={{
                            fontSize: 11,
                          }}
                        />

                        <YAxis
                          domain={[-1, 1]}
                          tick={{
                            fontSize: 11,
                          }}
                        />

                        <Tooltip
                          formatter={(
                            value
                          ) => [
                            Number(
                              value
                            ).toFixed(4),
                            "NDVI",
                          ]}
                        />

                        <Line
                          type="monotone"
                          dataKey="ndvi"
                          strokeWidth={3}
                          dot={{
                            r: 5,
                          }}
                          activeDot={{
                            r: 7,
                          }}
                        />

                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* NDVI RANGE */}

                  <div
                    style={{
                      display: "flex",
                      justifyContent:
                        "center",
                      flexWrap: "wrap",
                      gap: "20px",
                      marginTop: "15px",
                    }}
                  >
                    <span>
                      🟢{" "}
                      {t(
                        "healthyRange"
                      )}
                    </span>

                    <span>
                      🟠{" "}
                      {t(
                        "moderateRange"
                      )}
                    </span>

                    <span>
                      🔴{" "}
                      {t(
                        "poorRange"
                      )}
                    </span>
                  </div>

                  {/* RECENT HISTORY */}

                  <h3
                    style={{
                      marginTop: "25px",
                    }}
                  >
                    {t(
                      "recentNDVIAnalyses"
                    )}
                  </h3>

                  {healthHistory
                    .slice()
                    .reverse()
                    .map((item) => (
                      <div
                        className="history"
                        key={item.id}
                      >
                        <strong>
                          NDVI:{" "}
                          {Number(
                            item.ndvi
                          ).toFixed(4)}
                        </strong>

                        {" — "}

                        {translateHealthStatus(
                          item.health_status
                        )}

                        {" — "}

                        {item.created_at
                          ? new Date(
                              item.created_at
                            ).toLocaleString()
                          : "--"}
                      </div>
                    ))}
                </>
              )}

            </div>

            {/* MANUAL NDVI */}

            <div className="panel">

              <h3>
                {t("manualNDVI")}
              </h3>

              <p>
                {t(
                  "manualNDVIDescription"
                )}
              </p>

              <label>

                {t("ndvi")}

                <input
                  type="number"
                  min="-1"
                  max="1"
                  step="0.01"
                  value={ndvi}
                  onChange={(e) =>
                    setNdvi(
                      e.target.value
                    )
                  }
                />

              </label>

              <button
                className="primary"
                onClick={
                  analyzeHealth
                }
              >
                {t(
                  "analyzeManualNDVI"
                )}
              </button>

              {health &&
                !satelliteHealth && (
                  <div className="result">

                    <h2>
                      {translateHealthStatus(
                        health.health_status
                      )}
                    </h2>

                    <p>
                      {t("ndvi")}:{" "}
                      {Number(
                        health.ndvi
                      ).toFixed(4)}
                    </p>

                    {health.note && (
                      <p>
                        {translateHealthNote(health.note)}
                      </p>
                    )}

                  </div>
                )}

            </div>

          </section>
        )}

        {/* ================================================== */}
        {/* DISEASE DETECTION */}
        {/* ================================================== */}

        {page === "disease" && (
          <DiseaseDetection
            language={language}
          />
        )}
        {/* ================================================== */}
        {/* PEST DETECTION */}
        {/* ================================================== */}

        {page === "pest" && (
          <PestDetection
            language={language}
          />
        )}
        {/* ================================================== */}
        {/* AI CROP RESEARCH */}
        {/* ================================================== */}

        {page === "research" && (
          <ResearchAssistant
            language={language}
          />
        )}
        {/* ================================================== */}
        {/* VOICE ASSISTANT */}
        {/* ================================================== */}

        {page === "voice" && (
          <VoiceAssistant
            language={language}
          />
        )}

        {/* ================================================== */}
        {/* WEATHER */}
        {/* ================================================== */}

        {page === "weather" && (
          <section>

            <h2>
              🌤️{" "}
              {t("weatherPage")}
            </h2>

            {weather ? (
              <div className="result">

                <h2>
                  {weather.city}
                </h2>

                <p>
                  {t(
                    "temperature"
                  )}
                  :{" "}
                  {weather.temperature} °C
                </p>

                <p>
                  {t("humidity")}:{" "}
                  {weather.humidity}%
                </p>

                <p>
                  {translateWeatherDescription(weather.description)}
                </p>

                <button
                  className="primary"
                  onClick={
                    loadWeather
                  }
                >
                  {t(
                    "refreshWeather"
                  )}
                </button>

              </div>
            ) : (
              <button
                className="primary"
                onClick={
                  loadWeather
                }
              >
                {t("loadWeather")}
              </button>
            )}

          </section>
        )}

        {/* ================================================== */}
        {/* RECOMMENDATION HISTORY */}
        {/* ================================================== */}

        {page === "history" && (
          <section>

            <h2>
              📜{" "}
              {t(
                "recommendationHistory"
              )}
            </h2>

            {history.length === 0 ? (
              <p>
                {t("noHistory")}
              </p>
            ) : (
              history.map(
                (item, index) => (
                  <div
                    className="history"
                    key={
                      item.id ||
                      index
                    }
                  >
                    <strong>
                      {translateCropName(item.crop || item.recommended_crop)}
                    </strong>

                    {" — "}

                    {(
                      Number(
                        item.confidence
                      ) * 100
                    ).toFixed(1)}
                    %
                  </div>
                )
              )
            )}

          </section>
        )}

      </main>
    </div>
  );
}

// ============================================================
// STAT CARD
// ============================================================

function StatCard({
  icon,
  title,
  value,
  description,
}) {
  return (
    <div className="stat-card">

      <div className="stat-icon">
        {icon}
      </div>

      <div>
        <p className="stat-title">
          {title}
        </p>

        <h2>{value}</h2>

        <p className="stat-description">
          {description}
        </p>
      </div>

    </div>
  );
}

// ============================================================
// AUTH
// ============================================================

function Auth({
  title,
  fields,
  setFields,
  action,
  switcher,
  register,
  language,
  changeLanguage,
  t,
}) {
  return (
    <main className="auth">

      <div className="panel">

        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "10px",
          }}
        >
          <select
            value={language}
            onChange={(e) =>
              changeLanguage(
                e.target.value
              )
            }
          >
            <option value="en">
              🇬🇧 English
            </option>

            <option value="te">
              🇮🇳 తెలుగు
            </option>
          </select>
        </div>

        <h1>
          🌾 {title}
        </h1>

        <p>
          {t("smartSystem")}
        </p>

        {register && (
          <input
            placeholder={t("name")}
            value={fields.name}
            onChange={(e) =>
              setFields({
                ...fields,
                name: e.target.value,
              })
            }
          />
        )}

        <input
          placeholder={t("email")}
          type="email"
          value={fields.email}
          onChange={(e) =>
            setFields({
              ...fields,
              email: e.target.value,
            })
          }
        />

        <input
          placeholder={t("password")}
          type="password"
          value={fields.password}
          onChange={(e) =>
            setFields({
              ...fields,
              password: e.target.value,
            })
          }
        />

        <button
          className="primary"
          onClick={action}
        >
          {register
            ? t("register")
            : t("login")}
        </button>

        <button onClick={switcher}>
          {register
            ? t("alreadyAccount")
            : t(
                "createAccountButton"
              )}
        </button>

      </div>

    </main>
  );
}

// ============================================================
// START APPLICATION
// ============================================================

createRoot(
  document.getElementById("root")
).render(
  <App />
);